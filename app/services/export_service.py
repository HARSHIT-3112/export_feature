import grpc
import logging
from app.services.grpc import export_pb2, export_pb2_grpc
from app.utils.file_exporter import export_to_pdf, export_to_docx

logger = logging.getLogger(__name__)

class ExportService(export_pb2_grpc.ExportServiceServicer):
    async def ExportDocument(self, request, context):
        try:
            content = request.content
            meta = {"title": request.title or f"document_{request.document_id}"}
            style = dict(request.style)

            if not content:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing content")
                return export_pb2.ExportResponse()

            if request.export_type.lower() == "pdf":
                buffer = export_to_pdf(content, meta, request.include_cover_page, request.page_size, style)
                mime_type, ext = "application/pdf", "pdf"
            elif request.export_type.lower() == "docx":
                buffer = export_to_docx(content, meta, request.include_cover_page)
                mime_type, ext = "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid export_type")
                return export_pb2.ExportResponse()

            return export_pb2.ExportResponse(
                file_content=buffer.getvalue(),
                file_name=f"{meta['title']}.{ext}",
                mime_type=mime_type
            )

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return export_pb2.ExportResponse()

def register(server):
    export_pb2_grpc.add_ExportServiceServicer_to_server(ExportService(), server)
