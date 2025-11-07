# 📊 Report Data Analysis API (Demo)

## 🧭 Giới thiệu

Dự án này là một **API demo** được xây dựng bằng **FastAPI**, có chức năng:
- Nhận file dữ liệu kinh doanh (Excel, mã hóa Base64);
- Làm sạch và loại bỏ ngoại lệ (outlier);
- Tính toán các **metrics tài chính, marketing và khách hàng** theo thời gian;
- Trích xuất thông tin thời gian từ yêu cầu người dùng;
- (Trong bản chính thức) sinh biểu đồ trực quan và insights bằng mô hình ngôn ngữ (LLM).

> ⚠️ Phiên bản này **chỉ dùng cho mục đích demo**, chưa bao gồm phần thực thi `exec` sinh biểu đồ.

---

## ⚙️ Cấu trúc chính

### **1. Endpoint `/report/analyze`**

**Phương thức:** `POST`  
**Mô tả:** Xử lý file Excel từ người dùng, trích xuất khoảng thời gian, tính toán metrics và chuẩn bị dữ liệu cho bước trực quan hóa.

#### 🧩 Input
```json
{
  "input_data": "Phân tích doanh thu quý 3 năm 2024",
  "excel_base64": "<chuỗi base64 của file Excel>"
}
```

#### 🔁 Output
```json
{
  "visualize_b64_str": "<biểu đồ mã hóa Base64>",
  "mime-type": "image/png",
  "insights": "Doanh thu quý 3 tăng 12% so với quý 2, chủ yếu nhờ nhóm sản phẩm A và B."
}
```

> Trong bản demo này, phần `visualize_b64_str` và `insights` là placeholder.

---

## 🧮 File `metrics_cal.py`

Module này định nghĩa hàm:

```python
def metrics_calculate(df: pd.DataFrame, date_info: Date_Model) -> dict
```

### 🎯 Chức năng
Tính toán các chỉ số kinh doanh quan trọng (metrics) dựa trên dữ liệu đã làm sạch và thông tin thời gian được mô hình trích xuất.

### 📘 Logic chính
- Tạo bản sao dữ liệu (`df_dup`)
- Lọc dữ liệu theo khoảng thời gian (`date_info.month`, `date_info.year`)
- Gom nhóm dữ liệu theo `YearMonth`
- Tính toán các chỉ số theo:
  - **Tổng thể (intent = "Tổng thể")**
  - **Theo sản phẩm (intent = "Theo sản phẩm")**

---

## 📊 Các chỉ số được tính

| Nhóm | Chỉ số | Mô tả |
|------|--------|-------|
| **Doanh thu (Revenue)** | `total_revenue` | Tổng doanh thu |
| **Chi phí (Cost)** | `total_product_cost`, `total_marketing_cost`, `total_discount`, `total_cost` | Tổng chi phí sản xuất, marketing và khuyến mãi |
| **Lợi nhuận (Profit)** | `total_profit`, `profit_margin` | Tổng lợi nhuận và biên lợi nhuận |
| **Bán hàng (Sales)** | `online_order_rate`, `offline_order_rate` | Tỷ lệ đơn hàng online/offline |
| **Thanh toán (Payment)** | `card_rate`, `e_wallet_rate`, `cash_rate` | Tỷ lệ phương thức thanh toán |
| **Khách hàng (Customer)** | `customer_count` | Số lượng khách hàng duy nhất |
| **Theo sản phẩm (Product)** | `total_quantity` | Số lượng sản phẩm bán được |

---

## 📁 Cấu trúc thư mục

```
app/
├── api/
│   └── report_api.py              # API /report/analyze
├── models/
│   ├── date_extraction.py         # Mô hình trích xuất thông tin thời gian từ prompt
│   └── visual_insights_model.py   # Mô hình sinh biểu đồ & insights
├── utils/
│   ├── excel_handler.py           # Giải mã base64 → bytes → DataFrame
│   ├── remove_outlier.py          # Hàm loại bỏ ngoại lệ
│   └── metrics_cal.py             # Tính toán metrics
└── main.py                        # Entry point (chạy FastAPI)
```

---

## 🚀 Cách chạy demo

### 1️⃣ Cài đặt môi trường
```bash
pip install requirements
```

### 2️⃣ Khởi chạy server
```bash
uvicorn app.api.report_api:router --reload
```

### 3️⃣ Gửi yêu cầu mẫu
Dùng `curl` hoặc Postman:
```bash
curl -X POST "http://127.0.0.1:8000/report/analyze"   -H "Content-Type: application/json"   -d '{"input_data": "Tổng quan quý 1/2024", "excel_base64": "<chuỗi base64>"}'
```

---

## 📘 Ghi chú

- API này **cần LLM client (Gemini hoặc tương tự)** được cấu hình trong `app.state.gemini_client`.
- Hàm `remove_outliers` và `visualize_data` là các mô-đun độc lập, có thể tinh chỉnh theo từng bộ dữ liệu.
- Trong bản chính thức, phần `exec` sẽ được thay bằng cơ chế **safe function registry** để tránh rủi ro bảo mật.

---

## 🧠 Định hướng mở rộng

- Tự động nhận biết đơn vị tiền tệ và chuyển đổi.
- Hỗ trợ lọc theo khu vực, kênh bán hàng, nhóm sản phẩm.
- Thêm biểu đồ tương tác (Plotly / Altair).
- Triển khai mô hình tóm tắt insights bằng LLM thay vì prompt thủ công.

---

📍 **Tác giả:** Truong Bao  
🕓 **Phiên bản:** Demo 0.1  
🔗 **Ngôn ngữ:** Python 3.11, FastAPI, Pandas
