from pydantic import BaseModel

class Date_Model(BaseModel):
    month: list[str]
    year: list[str]
    intent: str
    # select_column: list[str]

def date_extraction(user_request: str, date_range:list, client) -> dict:
    prompt = f"""
    Bạn là một chuyện gia phân tích dữ liệu
    Dựa trên thông tin yêu cầu của người dùng, schema, column, metadata và khoảng thời gian của dữ liệu
    Hãy chọn ra khoảng thời gian cần lấy trong dữ liệu theo yêu cầu đó
    Đồng thời hãy trả về ý định của người dùng trong câu hỏi xem muốn so sánh tổng thể hay so sánh từng sản phẩm theo thời gian với 1 từ ngắn gọn là ["Tổng thể", "Theo sản phẩm"]
    
    Nếu yêu cầu của người dùng không có thông tin thời gian cụ thể, chỉ lấy quý gần nhất
    
    Khoảng thời gian:
    {date_range[0]} đến {date_range[-1]}

    Yêu cầu của người dùng:
    {user_request}

    Bạn cần trả về một file json với cấu trúc sau:
    month: các tháng được chọn theo yêu cầu của người dùng (list[str])
    year: năm được chọn theo yêu cầu của người dùng (list[str])
    intent: ý định của người dùng trong câu hỏi (str)

    Ví dụ:
    Giả sử thời gian trong khoảng tháng 1-2024 đến 12-2025
    Tôi cần so sánh doanh thu cùng kỳ với tháng trước: month: [12, 11], year: [2025]
    Tôi cần phân tích thông tin chi phí tháng này: month: [12], year: [2025]
    Tôi cần so sánh cùng kỳ theo tháng trong năm: month:[1,2,3,4,5,6,7,8,9,10,11,12], year:[2025]
    Tôi cần so sánh cùng kỳ theo năm: month:[1,2,3,4,5,6,7,8,9,10,11,12], year:[2024, 2025]

    Lưu ý:
    Thông tin trả về phải TRONG KHOẢNG THỜI GIAN ĐƯỢC CUNG CẤP

    Ví dụ
    Nếu trong dữ liệu cung cắp chỉ chứa thông tin trong một năm
    Mà người dùng có yêu cầu liên quan đến việc so sánh nhiều năm
    Ví dụ:
    Khoảng thời gian cung cấp chỉ có năm 2025
    Yêu cầu: So sánh doanh thu giữa các năm
    Hãy trả về: month: ["Không xác định"] và year: ["Không xác định"]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type":"application/json",
            "response_schema": Date_Model,
            "temperature":0.0
        }
    )

    return response.parsed


# Schema data:
#     {schema}

# Metadata:
# {metadata}
