from fastapi import APIRouter, Request, HTTPException

import pandas as pd
import pandasql as ps

import json

from pydantic import BaseModel

from typing import Dict, List, Optional

from app.utils.excel_handler import b64_to_bytes
# from app.utils.metrics_cal import metrics_calculate

from app.models.query_extraction import query_extraction
from app.models.visual_insights_model import visualize_data

from io import BytesIO

router = APIRouter(
    prefix="/report",
    tags=["Report Data Analysis"],
)

class InputRequest(BaseModel):
    input_data: str
    excel_base64: str

@router.post("/analyze")
async def analyze_report(req: InputRequest, request: Request):
    
    client = request.app.state.gemini_client

    #Xử lý HTTP Exception
    if client is None:
        raise HTTPException(status_code=500, detail="LLM client chưa được cấu hình trên server")
    if not req.input_data or not req.excel_base64:
        raise HTTPException(status_code=400, detail="Dữ liệu đầu vào không hợp lệ")
    
    # Đọc dữ liệu Excel từ chuỗi Base64
    excel_bytes = b64_to_bytes(req.excel_base64)
    excel_df = pd.read_excel(BytesIO(excel_bytes))

    # Clean and preprocess data
    excel_df = excel_df.dropna()

    # Chuẩn bị dữ liệu để gửi đến mô hình trích xuat thông tin thời gian
    date_range = excel_df["Date"].dt.date.unique()
    user_request = req.input_data
    column_info = {
        excel_df.columns[0]: "Tên công ty",
        excel_df.columns[1]: "Ngày giao dịch",
        excel_df.columns[2]: "Danh mục sản phẩm",
        excel_df.columns[3]: "Kênh bán hàng",
        excel_df.columns[4]: "Số lượng sản phẩm bán được",
        excel_df.columns[5]: "Giá mỗi đơn vị sản phẩm",
        excel_df.columns[6]: "Doanh thu từ giao dịch",
        excel_df.columns[7]: "Chi phí của giao dịch",
        excel_df.columns[8]: "Lợi nhuận giao dịch",
        excel_df.columns[9]: "Chi phí marketing cho giao dịch",
        excel_df.columns[10]: "ID khách hàng",
        excel_df.columns[11]: "Phương thức thanh toán",
        excel_df.columns[12]: "Mức giảm giá áp dụng"
    }
    metadata = excel_df.head(10).to_json(orient='records')
    schema = excel_df.info

    # Trích xuất thông tin thời gian
    sql_query = query_extraction(user_request, sorted(date_range), metadata, schema, column_info, client)

    if sql_query is None or sql_query.query.strip() == "":
        raise HTTPException(status_code=500, detail="Không thể trích xuất câu truy vấn từ yêu cầu của người dùng.")

    # Lấy thông tin dữ liệu bằng câu truy vấn SQL với pandasql
    result = ps.sqldf(sql_query.query, locals()).to_json(orient='records')
    print("SQL Query:", sql_query.query)

    # Đưa vào mô hình để vẽ và trích xuất insights
    visualize_insights = visualize_data(user_request, result, client)

    if visualize_insights is None:
        raise HTTPException(status_code=500, detail="Không thể trực quan hóa dữ liệu và lấy insights từ yêu cầu của người dùng.")

    # Thực thi hàm visualize_and_analyze
    try:
        exec(visualize_insights.code, globals())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cố trực quan hóa dữ liệu")
    
    # Chay ham vua duoc tao
    visualize_bytes, mime_type = visualize_and_analyze(result)# type: ignore

    if type(visualize_bytes) != str and type(mime_type) != str:
        raise HTTPException(status_code=500, detail="Hàm visualize_and_analyze không trả về đúng định dạng.")
    
    #Viết output
    output = {
        "visualize_b64_str": visualize_bytes,
        "mime-type": mime_type,
        "insights": visualize_insights.insight
    }

    return output