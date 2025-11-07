import pandas as pd
from app.models.date_extraction import Date_Model

def metrics_calculate(df: pd.DataFrame, date_info: Date_Model) -> dict:
    """
    Tính toán các metrics từ dữ liệu đã làm sạch dựa trên thông tin thời gian đã trích xuất.

    Args:
        df (pd.DataFrame): Dữ liệu đã làm sạch.
        date_info (Date_Model): Thông tin thời gian đã trích xuất.

    Returns:
        Dict: Các metrics tính toán được.
    """
    # Tạo bảng dữ liệu mới tránh tác đọc vào bảng dữ liệu gốc
    df_dup = df.copy()

    # Khởi tạo biến lưu trữ metrics
    metrics = {}

    # Thêm thông tin khoảng thời gian vào metrics
    metrics.update({
        "period": {
            "start_date": date_info.month[-1] + "-" + date_info.year[-1],
            "end_date": date_info.month[0] + "-" + date_info.year[0]
        }
    })

    # Thêm thông tin về đơn vị tiền tệ vào metrics
    metrics.update({
        "unit": "VND"
    })

    # Tạo cột YeatMonth để lọc dữ liệu
    df_dup["YearMonth"] = df_dup["Date"].dt.to_period("M")

    # Tạo tập hợp các khoảng thời gian YearMonth từ date_info cần để lọc
    target_periods = {
        pd.Period(year=int(i), month=int(j), freq='M')
        for i in date_info.year
        for j in date_info.month
    }

    # Lọc dữ liệu dựa trên các khoảng thời gian đã trích xuất
    filtered_df = df_dup[df_dup["YearMonth"].isin(target_periods)]

    # Gộp dữ liệu theo YearMonth để tính toán các metrics
    grouped = filtered_df.groupby("YearMonth")

    # Tính toán các metrics theo ý định của người dùng
    
    # Tính theo tổng thể theo thời gian
    if date_info.intent == "Tổng thể":
        for date, df_fil in grouped:
            metrics[str(date)] = {
                "data" : df_fil[date_info.select_column].to_json(orient='records'),
            }
    
    #Tính theo từng sản phẩm theo thời gian
    elif date_info.intent == "Theo sản phẩm":
        for date, df_fil in grouped:
            product = df["Product_Category"].unique()
            metrics[str(date)] = {}

            for p in product:
                df_prod = df_fil[df_fil["Product_Category"] == p]
                metrics[str(date)][p] = {
                    "data" : df_prod[date_info.select_column].to_json(orient='records'),
                }
            
    return metrics