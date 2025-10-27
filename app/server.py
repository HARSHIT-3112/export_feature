import grpc
import asyncio
import logging
from grpc_reflection.v1alpha import reflection   # ✅ add this import
from app.services import export_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serve():
    server = grpc.aio.server(
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ]
    )

    export_service.register(server)

    # ✅ Enable reflection
    SERVICE_NAMES = (
        export_service.export_pb2.DESCRIPTOR.services_by_name['ExportService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port("[::]:50051")
    return server

async def main():
    server = serve()
    logger.info("✅ ExportService gRPC Server started on port 50051 with reflection enabled")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(main())
