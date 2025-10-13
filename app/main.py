import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from google import genai

from app.routes import email_intent_finder

# Load biến môi trường từ file .env
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời ứng dụng FastAPI."""
    gemini_api_key = os.getenv("GENAI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GENAI_API_KEY is not set in environment variables")

    # Khởi tạo Gemini client và gắn vào state của app
    app.state.gemini_client = genai.Client(api_key=gemini_api_key)
    yield

# Khởi tạo ứng dụng FastAPI
app = FastAPI(lifespan=lifespan)

# Đăng ký router
app.include_router(email_intent_finder.router)
