# app/server.py
import asyncio
import logging
import signal
import grpc
from grpc_reflection.v1alpha import reflection
from app.services import export_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GRPC_PORT = 50051


def serve():
    server = grpc.aio.server(
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ]
    )

    # register service
    export_service.register(server)

    # register reflection
    try:
        svc_name = export_service.export_pb2.DESCRIPTOR.services_by_name["ExportService"].full_name
        SERVICE_NAMES = (svc_name, reflection.SERVICE_NAME)
        reflection.enable_server_reflection(SERVICE_NAMES, server)
        logger.info("gRPC reflection enabled")
    except Exception:
        logger.warning("Could not enable reflection; continuing without it")

    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    return server


async def _run():
    server = serve()
    await server.start()
    logger.info(f"🚀 ExportService gRPC Server started on port {GRPC_PORT}")

    # graceful shutdown on signals
    loop = asyncio.get_running_loop()
    stop = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: stop.set())
        except NotImplementedError:
            # windows
            pass

    await stop.wait()
    logger.info("Shutting down gRPC server...")
    await server.stop(5)


if __name__ == "__main__":
    asyncio.run(_run())
