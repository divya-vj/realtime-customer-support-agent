from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, analytics
from app.models.database import init_db

app = FastAPI(title="Customer Support Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])

@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized successfully!")

@app.get("/")
async def root():
    return {
        "message": "Customer Support Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
