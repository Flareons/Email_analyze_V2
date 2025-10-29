from pydantic import BaseModel
import json

class VisualizeModel(BaseModel):
    code: str
    insight: str

def visualize_data(user_request: str, metrics: str, client) -> dict:
    metrics = json.dumps(metrics)
    prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu.
    Nhiệm vụ 1: Viết hàm và lưu vào phần code trong json trả về
    Nhiệm vụ của bạn là viết ra một hàm Python ổn định, an toàn để trực quan hóa dữ liệu có thể chạy được bằng hàm exec(). 
    
    QUY TẮC CỐT LÕI:
    1. CHỈ được sử dụng thư viện: matplotlib.pyplot (plt), numpy, pandas, json, base64, io. Không sử dụng thêm thư viện khác
    2. Biểu đồ phải được trả về dưới dạng base64 bytes string trong biến **visual_bytes** và mime_type của biểu đồ ở biến **mime_type**.
    3. Lưu ảnh ở đường dẫn "email_classify/img/" với tên ảnh là "chart + yy-mm-dd-giờ:phút:giây". Ví dụ: chart2025-10-27-4:29:30
    4. KHÔNG ĐƯỢC PHÉP sử dụng biến có tên là **df** ở bất kỳ đâu.
    5. Mọi thư viện phải được import trong đoạn mã sinh ra.
    6. Tất cả phải gói gọn trong một hàm, không cần chạy hàm.
    7. Dùng đúng dữ liệu, nếu câu hỏi liên qua đến doanh thu thì dùng thông tin liên quan đến doanh thu, nếu liên quan đến chi phí thì dùng thông tin liên quan đến chi phí
    8. **Lưu ý: Không được hiển thị trục ở dạng số khoa học (scientific notation), phải hiển thị số đầy đủ có dấu phẩy phân cách hàng nghìn.**
    9. Hàm có tên visualize_and_analyze(json_str) với json_str là đầu vào giống dữ liệu metrics tổng hợp được cung cấp
    10. Chỉ sử dụng thông tin được cung cấp là (json_str) và các thư viện được cho phép để viết hàm
    11. Không dùng ticklabel_format() (nó chỉ an toàn với ScalarFormatter). Thay vào đó, format số xét từng trục bằng matplotlib.ticker.FuncFormatter hoặc StrMethodFormatter để hiển thị đầy đủ số và phân cách hàng nghìn.
    12. Không cần hiển thị biểu đồ chỉ cần trả về **visual_bytes** và **mime_type**
    13. Hàm không được trả về một json chứa **visual_bytes** và **mime_types** mà cần trả về **visual_bytes** và mime_type riêng biệt (phải viết "return visual_bytes, mime_types")
    
    YÊU CẦU CỦA NGƯỜI DÙNG:
    {user_request}
    
    DỮ LIỆU METRICS TỔNG HỢP (dưới dạng chuỗi JSON):
    {metrics}
    
    BƯỚC THỰC HIỆN CẦN CÓ TRONG CODE:
    1. Tải dữ liệu từ biến `json_str` (là chuỗi JSON) bằng `json.loads()`.
    2. Tạo một DataFrame **tạm thời** (ví dụ: `data_frame`) từ dữ liệu đã tải.
    3. Dựa trên các metric được cung cấp trong dữ liệu trực quan hóa dữ liệu theo yêu cầu của người dùng
    5. Lưu biểu đồ ở dạng base 64 string bytes
    6. Trả về 2 biến là **visual_bytes** biểu dồ ở dạng base 64 string bytes và **mime_type** là mime_type của nó

    Nhiệm vụ 2: Phân tích insight rồi lưu vào insight trong json trả về
    Nhiệm vụ của bạn là phân tích insights dựa trên data đã được cung cấp ở nhiệm vụ 1 và yêu cầu của người dùng
    
    Hãy trả lời dưới định dạng JSON với các trường sau:
    {{
        "code": "đoạn mã python hoàn chỉnh và đã kiểm lỗi",
        "insight": "các insights phân tích từ dữ liệu (ít nhất 3 gạch đầu dòng)"
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type":"application/json",
            "response_schema": VisualizeModel,
            "temperature":0.0
        }
    )

    return response.parsed