from fastapi import APIRouter, Response
import grpc
from app.services.grpc import export_pb2, export_pb2_grpc

router = APIRouter(prefix="/export", tags=["Export"])

@router.post("/")
async def export_document(payload: dict):
    """HTTP wrapper around the gRPC ExportService."""
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = export_pb2_grpc.ExportServiceStub(channel)

        # Build the gRPC request from HTTP JSON payload
        request = export_pb2.ExportRequest(
            document_id=payload.get("document_id", ""),
            title=payload.get("title", ""),
            author=payload.get("author", ""),                # ✅ added
            category=payload.get("category", ""),            # ✅ added
            tags=payload.get("tags", []),                    # ✅ added
            created_at=payload.get("created_at", ""),        # ✅ added
            content=payload.get("content", ""),
            export_type=payload.get("export_type", "pdf"),
            page_size=payload.get("page_size", "A4"),
            include_cover_page=payload.get("include_cover_page", False)
        )

        response = await stub.ExportDocument(request)

        # Return as downloadable file (Blob)
        return Response(
            content=response.file_content,
            media_type=response.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{response.file_name}"'
            }
        )
