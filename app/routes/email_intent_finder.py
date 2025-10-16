# app/routers/email_intent_finder.py

from typing import Dict, List, Optional

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from app.models.analyze_model import analyze
from app.db.base import SessionDep, Email_Table
from datetime import datetime


router = APIRouter(
    prefix="/email_intent_finder",
    tags=["Email intent analysis"],
)

class EmailRequest(BaseModel):
    email: Optional[str] = None
    attachment: Optional[List[Dict]] = None

class EmailItems(BaseModel):
    items: List[EmailRequest]

@router.get("/")
async def root():
    return {"message": "Email Intent Finder API is running"}

@router.post("/email")
async def analyze_email(req: EmailItems, request: Request, Session: SessionDep):
    """
    Nhận một danh sách EmailRequest, mỗi email có thể kèm attachments (list of dict).
    Trả về list kết quả gồm intent, sumarize và attachments (phân tích).
    """

    client = request.app.state.gemini_client

    results = []

    if not req.items or len(req.items) == 0:
        raise HTTPException(status_code=400, detail="Danh sách email trống hoặc không hợp lệ")

    try:
        for item in req.items:
            if item.email is None and item.attachment is None:
                timestamp = datetime.now().isoformat()
                intent = "Không xác định"
                sumarize = "Email trống"
                attachments = "Không có tệp đính kèm"
                prompt_token = 0
                generate_token = 0
                thought_token = 0
                total_token = 0

                email_record = Email_Table(**{
                    "Timestamp": timestamp,
                    "sumarize": sumarize,
                    "attachments_analyze": attachments,
                    "intent": intent,
                    "prompt_token": prompt_token,
                    "generate_token": generate_token,
                    "thought_token": thought_token,
                    "total_token": total_token
                })

                Session.add(email_record)
                Session.commit()
                Session.refresh(email_record)

                results.append({
                    "response": {
                        "intent": "Không xác định",
                        "sumarize": "Email trống",
                        "attachments": "Khong có tệp đính kèm"
                    },
                    "prompt_token": 0,
                    "generate_token": 0,
                    "thought_token": 0,
                    "timestamp": timestamp
                })
                continue

            result, prompt_token, generate_token, thought_token, timestamp=analyze(e=item, client=client)

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

            results.append(json_result)

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

