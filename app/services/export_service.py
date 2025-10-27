# app/services/export_service.py
import grpc
import logging
from app.services.grpc import export_pb2, export_pb2_grpc
from app.utils.file_exporter import export_to_pdf, export_to_docx

logger = logging.getLogger(__name__)


class ExportService(export_pb2_grpc.ExportServiceServicer):
    async def ExportDocument(self, request, context):
        try:
            logger.info(f"📄 Export request received for: {getattr(request, 'document_id', 'unknown')}")

            # Collect metadata safely with defaults
            meta = {
                "document_id": getattr(request, "document_id", "") or "Untitled",
                "title": getattr(request, "title", "") or "Untitled Document",
                "author": getattr(request, "author", "") or "Unknown",
                "category": getattr(request, "category", "") or "General",
                "tags": list(getattr(request, "tags", [])) or [],
                "created_at": getattr(request, "created_at", "") or "-",
            }

            # Content validation
            content = getattr(request, "content", "")
            if not content or not content.strip():
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Empty content")
                return export_pb2.ExportResponse()

            # Required fields check
            required = ["document_id", "title", "content"]
            missing = [f for f in required if not getattr(request, f, "").strip()]
            if missing:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Missing required fields: {', '.join(missing)}")
                return export_pb2.ExportResponse()

            # Choose exporter
            export_type = (getattr(request, "export_type", "") or "pdf").lower()
            if export_type == "pdf":
                buffer = export_to_pdf(content, meta, request.include_cover_page, request.page_size)
                mime_type = "application/pdf"
                ext = "pdf"
            elif export_type in ("doc", "docx"):
                buffer = export_to_docx(content, meta, request.include_cover_page)
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ext = "docx"
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid export type: expected 'pdf' or 'docx'")
                return export_pb2.ExportResponse()

            # return bytes as protobuf bytes
            return export_pb2.ExportResponse(
                file_content=buffer.getvalue(),
                file_name=f"{meta['title']}.{ext}",
                mime_type=mime_type
            )

        except Exception as e:
            logger.exception("❌ Export failed")
            # send generic internal error with message
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return export_pb2.ExportResponse()


def register(server):
    export_pb2_grpc.add_ExportServiceServicer_to_server(ExportService(), server)
