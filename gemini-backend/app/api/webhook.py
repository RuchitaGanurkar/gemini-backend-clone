from fastapi import APIRouter

router = APIRouter(prefix="/webhook", tags=["Webhook"])

@router.get("/health")
def webhook_health():
    return {"status": "webhook service is running"}
