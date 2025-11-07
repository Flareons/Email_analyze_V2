from pydantic import BaseModel
import json

class VisualizeModel(BaseModel):
    code: str
    insight: str

def visualize_data(user_request: str, metrics: str, client) -> dict:
    metrics = json.dumps(metrics)
    prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu đồng thời là một lập trình viên.
    Nhiệm vụ 1: Viết hàm và lưu vào phần code trong json trả về
    Nhiệm vụ của bạn là viết ra một hàm Python ổn định, an toàn để trực quan hóa dữ liệu có thể chạy được bằng hàm exec(). 
    
    QUY TẮC CỐT LÕI CHO VIỆC VIẾT HÀM:
    1. CHỈ được sử dụng thư viện: matplotlib.pyplot (plt), numpy, pandas, json, base64, io. Không sử dụng thêm thư viện khác
    2. Biểu đồ phải được trả về dưới dạng base64 bytes string trong biến **visual_bytes** và mime_type của biểu đồ ở biến **mime_type**.
    3. KHÔNG ĐƯỢC PHÉP sử dụng biến có tên là **df** ở bất kỳ đâu.
    4. Mọi thư viện phải được import trong đoạn mã sinh ra.
    5. Tất cả phải gói gọn trong một hàm, không cần chạy hàm.
    6. Dùng đúng dữ liệu, nếu câu hỏi liên qua đến doanh thu thì dùng thông tin liên quan đến doanh thu, nếu liên quan đến chi phí thì dùng thông tin liên quan đến chi phí
    7. **Lưu ý: Không được hiển thị trục ở dạng số khoa học (scientific notation), phải hiển thị số đầy đủ có dấu phẩy phân cách hàng nghìn.**
    8. Hàm có tên visualize_and_analyze(json_str) với json_str là đầu vào giống dữ liệu metrics tổng hợp được cung cấp
    9. Chỉ sử dụng thông tin được cung cấp là (json_str) và các thư viện được cho phép để viết hàm
    10. Không dùng ticklabel_format() (nó chỉ an toàn với ScalarFormatter) và IndexFormatter. Format số bằng FuncFormatter hoặc StrMethodFormatter, còn nhãn chuỗi thì dùng set_xticks / set_xticklabels.
    11. Không cần hiển thị biểu đồ chỉ cần trả về **visual_bytes** và **mime_type**
    12. Hàm không được trả về một json chứa **visual_bytes** và **mime_types** mà cần trả về **visual_bytes** và mime_type riêng biệt (phải viết "return visual_bytes, mime_types")
    13. Phải viết theo cấu trúc code của python, không được viết code như một đoạn văn
    14. Các trường và title của bảng phải để tiếng việt.
    15. Vẽ không quá một bảng biểu đồ

    QUY TẮC CỐT LÕI CHO VIỆC VIẾT INSIGHTS:
    1. CHỈ DỰA TRÊN DỮ LIỆU CUNG CẤP: Tuyệt đối không suy diễn, giả định hay sử dụng thông tin từ bên ngoài báo cáo được cung cấp. Mọi kết luận phải có căn cứ rõ ràng từ dữ liệu.
    2. LƯỢNG HÓA SO SÁNH: Khi chỉ ra sự khác biệt, thay đổi, hoặc xu hướng BẮT BUỘC phải trích dẫn số liệu.
    3. TRÍCH DẪN SỐ LIỆU CỤ THỂ: Mọi nhận định, xu hướng, hoặc điểm dữ liệu quan trọng phải được lượng hóa và trích dẫn số liệu cụ thể vào trong câu văn.
    4. PHÂN TÍCH 'TẠI SAO': Không chỉ báo cáo 'Cái gì đã xảy ra' (What) mà phải phân tích 'TẠI SAO' (Why) điều đó xảy ra dựa trên mối tương quan giữa các số liệu khác nhau trong báo cáo.
    5. TÍNH HÀNH ĐỘNG: Mỗi insight phải ngụ ý một HÀM Ý KINH DOANH (Implication) hoặc GỢI Ý HÀNH ĐỘNG cụ thể. Insight không có hành động đề xuất là insight yếu.
    6. GIỌNG VĂN CHUYÊN NGHIỆP: Sử dụng ngôn ngữ khách quan, trang trọng, cô đọng. Tránh các từ ngữ cảm tính, cường điệu (ví dụ: "cực kỳ ấn tượng," "tuyệt vời") mà thay bằng các từ ngữ lượng hóa (ví dụ: "vượt mục tiêu 20%," "tăng trưởng mạnh").
    7. TÓM TẮT ĐẦU VÀO & ĐƠN VỊ: Bắt buộc kiểm tra lại đơn vị của số liệu ($, VND, % điểm phần trăm, lượt) và sử dụng đơn vị chính xác trong câu insights để tránh hiểu lầm.
    8. CẢNH BÁO RỦI RO: Bên cạnh các điểm tích cực, cần chỉ ra các điểm dữ liệu tiêu cực, các chỉ số dưới mục tiêu, hoặc các rủi ro tiềm ẩn (ví dụ: "Mặc dù doanh thu tăng, chi phí CAC cũng tăng 35% cho thấy hiệu suất chi tiêu đang giảm").

    
    YÊU CẦU CỦA NGƯỜI DÙNG:
    {user_request}
    
    DỮ LIỆU METRICS TỔNG HỢP (dưới dạng chuỗi JSON):
    {metrics}
    
    BƯỚC THỰC HIỆN CẦN CÓ TRONG CODE:
    1. Tải dữ liệu từ biến `json_str` (là chuỗi JSON) bằng `json.loads()`.
    2. Tạo một DataFrame **tạm thời** (ví dụ: `data_frame`) từ dữ liệu đã tải.
    3. Dựa trên các metric được cung cấp trong dữ liệu trực quan hóa dữ liệu theo yêu cầu của người dùng với những biểu đồ cho phép dưới đây:
        Line chart --> Sử dụng với các doanh thu hay chi phí theo thời gian
        Bar chart --> Lợi nhuận theo thời gian 
        Bar or pie chart --> Doanh thu theo nhóm
        Growth chart --> Tốc độ tăng trưởng doanh thu
        Margin chart --> Tỷ suất lợi nhuận
    4. Lưu biểu đồ ở dạng base 64 string bytes
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
    print(response)
    return response.parsed

#Xử lý sao cho AI flexible nhất, không giới hạn quá data