from fastapi import FastAPI

app = FastAPI(
    title="Notification Service",
    description="Serviço de notificações multicanal com DDD",
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
