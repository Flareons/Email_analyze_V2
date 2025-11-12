from pydantic import BaseModel

class QueryModel(BaseModel):
    query: str
    # select_column: list[str]

def query_extraction(user_request: str, date_range:list, metadata, schema, column_info, client) -> dict:
    prompt = f"""
    Bạn là chuyên gia kỹ sư dữ liệu, chuyên sinh SQL chuẩn SQLite (pandasql) để phục vụ trực quan hóa dữ liệu với matplotlib.

    Nhiệm vụ:
    - Phân tích yêu cầu của người dùng ({user_request}) bằng ngôn ngữ tự nhiên.
    - Sinh **DUY NHẤT câu SQL hoàn chỉnh**, chạy trực tiếp trong pandasql, trả về toàn bộ dữ liệu cần thiết cho biểu đồ.
    - Nếu user hỏi "top N" hoặc "sản phẩm bán chạy nhất", luôn lấy ít nhất **3 dòng**, không dùng LIMIT 1.
    - Luôn trả về dữ liệu đầy đủ để vẽ **trục X** (thời gian, danh mục, khách hàng...) và **trục Y** (doanh thu, số lượng, chi phí, v.v.).
    - Với các yêu cầu so sánh cùng kỳ, **tự động lấy dữ liệu tháng/quý/năm trước** để so sánh.
    - Group BY chỉ chứa **cột hoặc biểu thức**, không đặt aggregate function. Nếu cần lọc theo tổng hợp, dùng HAVING.

    **Ví dụ pattern AI nên theo (ít nhất 2 ví dụ SQL):**

    **Pattern 1: So sánh cùng kỳ theo quý**  
    WITH quarterly AS (
        SELECT 
            strftime('%Y', date) AS year,
            (CAST(strftime('%m', date) AS INTEGER)-1)/3+1 AS quarter,
            SUM(revenue) AS total_revenue
        FROM excel_df
        GROUP BY year, quarter
    )
    SELECT 
        curr.year,
        curr.quarter,
        curr.total_revenue AS revenue_now,
        prev.total_revenue AS revenue_last_year,
        ROUND((curr.total_revenue - prev.total_revenue) * 100.0 / prev.total_revenue, 2) AS pct_change
    FROM quarterly AS curr
    LEFT JOIN quarterly AS prev
        ON curr.quarter = prev.quarter AND curr.year = prev.year + 1
    ORDER BY curr.year, curr.quarter;

    **Pattern 2: Phân tích đa dạng sản phẩm, chi phí, khách hàng**  

    a) So sánh doanh thu hai sản phẩm A và B theo tháng:
    WITH monthly_products AS (
        SELECT 
            strftime('%Y-%m', date) AS month,
            product_name,
            SUM(revenue) AS total_revenue
        FROM excel_df
        WHERE product_name IN ('A','B')
        GROUP BY month, product_name
    )
    SELECT 
        month,
        product_name,
        total_revenue
    FROM monthly_products
    ORDER BY month, product_name;

    b) Top 3 khách hàng mua nhiều nhất trong tháng:
    SELECT 
        customer_id,
        SUM(revenue) AS total_revenue
    FROM excel_df
    WHERE strftime('%Y-%m', date) = '2024-10'
    GROUP BY customer_id
    ORDER BY total_revenue DESC
    LIMIT 3;

    c) Chi phí marketing theo kênh bán hàng theo quý:
    WITH quarterly_cost AS (
        SELECT 
            (CAST(strftime('%m', date) AS INTEGER)-1)/3+1 AS quarter,
            marketing_channel,
            SUM(cost) AS total_cost
        FROM excel_df
        GROUP BY quarter, marketing_channel
    )
    SELECT 
        quarter,
        marketing_channel,
        total_cost
    FROM quarterly_cost
    ORDER BY quarter, marketing_channel;

    Ràng buộc kỹ thuật:
    - SQL phải chạy trực tiếp trong pandasql / SQLite.
    - Trả về đầy đủ cột để vẽ biểu đồ (trục X / trục Y). 
    - Tên bảng: `excel_df`.
    - Cột và schema: {column_info}, {schema}.
    - Metadata ví dụ 10 dòng đầu: {metadata}.
    - Khoảng thời gian dữ liệu: {date_range[0]} đến {date_range[-1]}.
    - Các câu hỏi liên quan đến năm hiện tại thì chỉ cần lấy dữ liệu của năm hiện tại theo khoảng thời gian mà người dùng yêu cầu.
    Ví dụ: 
    Nếu user hỏi "Doanh thu từ tháng 1 đến tháng 6 năm nay", chỉ lấy dữ liệu từ tháng 1 đến tháng 6 của năm hiện tại.
    Nếu user hỏi "So sánh cùng kỳ theo quý hay tháng của năm nay", chỉ lấy dữ liệu từng quý hay tháng của năm hiện tại.


    Chỉ trả về câu SQL, không giải thích thêm.

    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type":"application/json",
            "response_schema": QueryModel,
            "temperature":0.0
        }
    )

    return response.parsed