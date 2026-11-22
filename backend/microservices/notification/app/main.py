
"""Notification microservice - FastAPI with Eureka and Actuator endpoints."""

import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
import py_eureka_client.eureka_client as eureka_client

from app.routers import notification


# =====================================
# CONFIGURATION
# =====================================

PORT = int(os.getenv("PORT", "8084"))

EUREKA_SERVER = os.getenv(
    "EUREKA_SERVER",
    "http://localhost:8761/eureka"
)

START_TIME = time.monotonic()
total_requests = 0


# =====================================
# EUREKA CLIENT
# =====================================

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


# =====================================
# FASTAPI APPLICATION
# =====================================

app = FastAPI(
    title="Notification Microservice API",
    version="1.0.0",
    description=(
        "Notification microservice (Python / FastAPI, no database). "
        "Only the hello endpoint is implemented; "
        "the notification logic is to be developed by students."
    ),
    contact={"name": "Badia Abouhdid"},
    servers=[
        {
            "url": f"http://localhost:{PORT}",
            "description": "Local"
        }
    ],
    docs_url="/swagger-ui",
    openapi_url="/v3/api-docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# =====================================
# METRICS MIDDLEWARE
# =====================================

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    global total_requests

    total_requests += 1
    response = await call_next(request)

    return response


# =====================================
# ACTUATOR - HEALTH
# =====================================

@app.get("/actuator/health", tags=["Actuator"])
def actuator_health():
    return {
        "status": "UP",
        "components": {
            "notification": {
                "status": "UP"
            }
        }
    }


# =====================================
# ACTUATOR - INFO
# =====================================

@app.get("/actuator/info", tags=["Actuator"])
def actuator_info():
    return {
        "app": {
            "name": "notification",
            "version": "1.0.0",
            "description": "JobBoard Notification Microservice",
            "technology": "Python / FastAPI"
        }
    }


# =====================================
# ACTUATOR - METRICS
# =====================================

@app.get("/actuator/metrics", tags=["Actuator"])
def actuator_metrics():
    return {
        "service": "notification",
        "uptime_seconds": round(
            time.monotonic() - START_TIME, 2
        ),
        "cpu": {
            "process_cpu_seconds": round(
                time.process_time(), 4
            )
        },
        "http": {
            "total_requests": total_requests
        }
    }


# =====================================
# NOTIFICATION ROUTES
# =====================================

app.include_router(notification.router)


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
    )
