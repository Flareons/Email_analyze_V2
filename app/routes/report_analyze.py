from fastapi import APIRouter, Request, HTTPException

import pandas as pd

import json

from pydantic import BaseModel

from typing import Dict, List, Optional

from app.utils.excel_handler import b64_to_bytes
from app.utils.remove_outlier import remove_outliers
from app.utils.metrics_cal import metrics_calculate

from app.models.date_extraction import date_extraction
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

    # Remove outliers (Xem lại)
    excel_categorical = excel_df["Product_Category"].unique()
    for i in excel_categorical:
        subset = excel_df[excel_df["Product_Category"] == i]
        cleaned_subset = remove_outliers(subset)
        excel_df = pd.concat([excel_df[excel_df["Product_Category"] != i], cleaned_subset])

    # Chuẩn bị dữ liệu để gửi đến mô hình trích xuat thông tin thời gian
    date_range = excel_df["Date"].dt.date.unique()
    user_request = req.input_data

    # schema = {
    #     excel_df.columns[0]: "Tên công ty",
    #     excel_df.columns[1]: "Ngày giao dịch",
    #     excel_df.columns[2]: "Danh mục sản phẩm",
    #     excel_df.columns[3]: "Kênh bán hàng",
    #     excel_df.columns[4]: "Số lượng sản phẩm bán được",
    #     excel_df.columns[5]: "Giá mỗi đơn vị sản phẩm",
    #     excel_df.columns[6]: "Doanh thu từ giao dịch",
    #     excel_df.columns[7]: "Chi phí của giao dịch",
    #     excel_df.columns[8]: "Lợi nhuận giao dịch",
    #     excel_df.columns[9]: "Chi phí marketing cho giao dịch",
    #     excel_df.columns[10]: "ID khách hàng",
    #     excel_df.columns[11]: "Phương thức thanh toán",
    #     excel_df.columns[12]: "Mức giảm giá áp dụng"
    # }
    # schema = json.dumps(schema)
    # metadata = excel_df.head(10).to_json(orient='records')

    # Trích xuất thông tin thời gian
    date_info = date_extraction(user_request, sorted(date_range), client)

    print(date_info.month)
    print(date_info.year)
    print(date_info.intent)

    # Xử lý HTTP Exception với đầu vào không hợp lệ
    if date_info.month[0]=="Không xác định" and date_info.year[0]=="Không xác định":
        raise HTTPException(status_code=400, detail="Dữ liệu và yêu cầu không đồng nhất.")

    # Tính toán metrics từ dữ liệu đã làm sạch theo thông tin thời gian
    metrics = metrics_calculate(excel_df, date_info)

    # Đưa vào mô hình để vẽ và trích xuất insights
    visualize_insights = visualize_data(user_request, metrics, client)

    # Thực thi hàm visualize_and_analyze
    exec(visualize_insights.code, globals())

    # Chay ham vua duoc tao
    visualize_bytes, mime_type = visualize_and_analyze(json.dumps(metrics))# type: ignore

    #Viết output
    output = {
        "visualize_b64_str": visualize_bytes,
        "mime-type": mime_type,
        "insights": visualize_insights.insight
    }

    return output