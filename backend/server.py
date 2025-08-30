from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from api import auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Resume Assist API"
    }


@app.get("/ping")
async def ping(request: Request):
    client_send_time = request.query_params.get("t")
    server_time = time.time() * 1000 

    if client_send_time:
        try:
            client_send_time = float(client_send_time)
            latency = server_time - client_send_time
        except ValueError: latency = None
    else: latency = None

    return {
        "server_time_ms": round(server_time, 2),
        "ping_ms": round(latency, 2) if latency is not None else "Send 't' param to measure latency"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
