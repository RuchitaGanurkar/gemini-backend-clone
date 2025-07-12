from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user, chatroom, subscription, webhook
from app.database import engine
from app.models import user as user_models, chatroom as chatroom_models, subscription as subscription_models

# Create database tables
user_models.Base.metadata.create_all(bind=engine)
chatroom_models.Base.metadata.create_all(bind=engine)
subscription_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gemini Backend Clone",
    description="Backend system for Gemini-style AI chatrooms with subscription management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chatroom.router)
app.include_router(subscription.router)
app.include_router(webhook.router)

@app.get("/")
def root():
    return {"message": "Gemini Backend Clone API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
