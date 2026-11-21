
"""Notification microservice - FastAPI with Eureka Client."""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
import py_eureka_client.eureka_client as eureka_client

from app.routers import notification

PORT = int(os.getenv("PORT", "8084"))
EUREKA_SERVER = os.getenv(
    "EUREKA_SERVER",
    "http://localhost:8761/eureka"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register NOTIFICATION in Eureka at startup
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,
        app_name="NOTIFICATION",
        instance_port=PORT,
    )

    print(f"NOTIFICATION registered in Eureka on port {PORT}")

    yield

    # Stop Eureka client when FastAPI shuts down
    await eureka_client.stop_async()
    print("NOTIFICATION Eureka client stopped")


app = FastAPI(
    title="Notification Microservice API",
    version="1.0.0",
    description=(
        "Notification microservice (Python / FastAPI, no database). "
        "Only the hello endpoint is implemented; "
        "the notification logic is to be developed by students."
    ),
    contact={"name": "Badia Abouhdid"},
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local"}],
    docs_url="/swagger-ui",
    openapi_url="/v3/api-docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(notification.router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
    )
