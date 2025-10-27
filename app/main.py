import asyncio
from app.server import serve

from fastapi import FastAPI
from app.http.export_router import router as export_router

app = FastAPI(title="Export Gateway")
app.include_router(export_router)


async def main():
    server = serve()
    print("🚀 ExportService standalone gRPC server is running on port 50051")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(main())
