import grpc
import logging
from app.services.grpc import export_pb2, export_pb2_grpc
from app.utils.file_exporter import export_to_pdf, export_to_docx

logger = logging.getLogger(__name__)

class ExportService(export_pb2_grpc.ExportServiceServicer):
    async def ExportDocument(self, request, context):
        try:
            logger.info(f"Export request for document: {request.document_id}")

            content = request.content
            meta = {"title": request.title or f"document_{request.document_id}"}
            export_type = request.export_type.lower()
            include_cover_page = request.include_cover_page
            page_size = request.page_size or "A4"

            if not content:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing content in request")
                return export_pb2.ExportResponse()

            if export_type == "pdf":
                buffer = export_to_pdf(content, meta, include_cover_page, page_size)
                mime_type, ext = "application/pdf", "pdf"
            elif export_type == "docx":
                buffer = export_to_docx(content, meta, include_cover_page)
                mime_type, ext = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "docx",
                )
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid export type: must be pdf or docx")
                return export_pb2.ExportResponse()

            file_name = f"{meta['title']}.{ext}"
            return export_pb2.ExportResponse(
                file_content=buffer.getvalue(),
                file_name=file_name,
                mime_type=mime_type,
            )

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return export_pb2.ExportResponse()


def register(server):
    export_pb2_grpc.add_ExportServiceServicer_to_server(ExportService(), server)
