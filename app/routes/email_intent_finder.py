# app/routers/email_intent_finder.py

from typing import Dict, List, Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.models.analyze_model import analyze
from app.db.base import SessionDep, Email_Table
from datetime import datetime

# Định nghĩa router cho email intent finder
router = APIRouter(
    prefix="/email_intent_finder",
    tags=["Email intent analysis"],
)

# Định nghĩa các model Pydantic cho request và response
class EmailRequest(BaseModel):
    email: Optional[str] = None
    attachment: Optional[List[Dict]] = None

# class EmailItems(BaseModel):
#     items: List[EmailRequest]

# Root endpoint để kiểm tra API có hoạt động không
@router.get("/")
async def root():
    return {"message": "Email Intent Finder API is running"}

# Endpoint chính để phân tích email và trích xuất intent
@router.post("/email")
async def analyze_email(req: EmailRequest, request: Request, Session: SessionDep):
    """
    Nhận một danh sách EmailRequest, mỗi email có thể kèm attachments (list of dict).
    Trả về list kết quả gồm intent, sumarize và attachments (phân tích).
    """

    # Lấy Gemini client từ state của ứng dụng
    client = request.app.state.gemini_client

    results = []

    if client is None:
        raise HTTPException(status_code=500, detail="LLM client chưa được cấu hình trên server")

    if req.email == None and req.attachment == None:
        raise HTTPException(status_code=400, detail="Danh sách email trống hoặc không hợp lệ")

    try:
        email = req.email
        attachment = req.attachment
        json_result = None
        # Gọi hàm analyze để phân tích email và attachments
        result, prompt_token, generate_token, thought_token, timestamp=analyze(email, attachment, client=client)
        total_token = prompt_token + generate_token + thought_token

        email_record = Email_Table(**{
            "Timestamp": timestamp,
            "sumarize": result.sumarize,
            "attachments_analyze": ";\n ".join(result.attachments) if result.attachments else "Không có tệp đính kèm",
            "intent": result.intent,
            "prompt_token": prompt_token,
            "generate_token": generate_token,
            "thought_token": thought_token,
            "total_token": total_token
        })

        Session.add(email_record)
        Session.commit()
        Session.refresh(email_record)

        json_result={
            "response": result,
            "prompt_token": prompt_token,
            "generate_token": generate_token,
            "thought_token": thought_token
        }

        return(json_result)

    except ValueError as e:
        # Nếu hàm analyze gặp lỗi ValueError, ném HTTPException 500
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích email: {str(e)}")
    
    except Exception as e:
        # Bắt tất cả các lỗi khác
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi không xác định trong server")

    return results


    
    # Cách xử lý nhiều kiểu attachment:
    # Chia làm 2 phần xử lý:
    # 1. Xử lý attachment video: blob
    #     Với video: Xử lý riêng dạng Blob
    # 2. Xử lý attachment image/audio/document: bytes
    #     Với hình ảnh: chuyển sang binary cho mô hình có thể hiểu được
    #     Với audio: Chuyển sang text (nếu có thể) rồi mới phân tích hoặc đổi sang bytes và xử lý
    #     Với các file documents như word, excel, etc: chuyển sang pdf rồi chuyển sang bytes và đưa vào mô hình

