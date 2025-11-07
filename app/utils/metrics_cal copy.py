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
            total_revenue = df_fil["Revenue"].sum()
            min_revenue = df_fil["Revenue"].min()
            max_revenue = df_fil["Revenue"].max()
            mean_revenue = df_fil["Revenue"].mean()
            total_cost = df_fil["Cost"].sum()
            min_cost = df_fil["Cost"].min()
            max_cost = df_fil["Cost"].max()
            mean_cost = df_fil["Cost"].mean()
            total_profit = df_fil["Profit"].sum()
            min_profit = df_fil["Profit"].min()
            max_profit = df_fil["Profit"].max()
            mean_profit = df_fil["Profit"].mean()
            total_marketing_cost = df["Marketing_Cost"].sum()
            max_marketing_cost = df["Marketing_Cost"].max()
            min_marketing_cost = df["Marketing_Cost"].min()
            mean_marketing_cost = df["Marketing_Cost"].mean()
            profit_margin = ((total_profit + total_marketing_cost) / total_revenue * 100) if total_revenue != 0 else 0
            

            metrics[str(date)] = {
                "total_revenue": total_revenue,
                "min_revenue": min_revenue,
                "max_revenue": max_revenue,
                "mean_revenue": mean_revenue,
                "total_cost": total_cost,
                "min_cost": min_cost,
                "max_cost": max_cost,
                "mean_cost": mean_cost,
                "total_profit": total_profit,
                "min_profit": min_profit,
                "max_profit": max_profit,
                "mean_profit": mean_profit,
                "total_marketing_cost": total_marketing_cost,
                "min_marketing_cost": min_marketing_cost,
                "max_marketing_cost": max_marketing_cost,
                "mean_marketing_cost": mean_marketing_cost,
                "profit_margin": profit_margin
            }
    
    #Tính theo từng sản phẩm theo thời gian
    elif date_info.intent == "Theo sản phẩm":
        for date, df_fil in grouped:
            product = df["Product_Category"].unique()
            metrics[str(date)] = {}

            for p in product:
                df_prod = df_fil[df_fil["Product_Category"] == p]
                total_revenue = df_prod["Revenue"].sum()
                min_revenue = df_prod["Revenue"].min()
                max_revenue = df_prod["Revenue"].max()
                mean_revenue = df_prod["Revenue"].mean()
                total_cost = df_prod["Cost"].sum()
                min_cost = df_prod["Cost"].min()
                max_cost = df_prod["Cost"].max()
                mean_cost = df_prod["Cost"].mean()
                total_profit = df_prod["Profit"].sum()
                min_profit = df_prod["Profit"].min()
                max_profit = df_prod["Profit"].max()
                mean_profit = df_prod["Profit"].mean()
                total_marketing_cost = df_prod["Marketing_Cost"].sum()
                max_marketing_cost = df_prod["Marketing_Cost"].max()
                min_marketing_cost = df_prod["Marketing_Cost"].min()
                mean_marketing_cost = df_prod["Marketing_Cost"].mean()
                profit_margin = ((total_profit + total_marketing_cost) / total_revenue * 100) if total_revenue != 0 else 0

                metrics[str(date)][p] = {
                    "total_revenue": total_revenue,
                    "min_revenue": min_revenue,
                    "max_revenue": max_revenue,
                    "mean_revenue": mean_revenue,
                    "total_cost": total_cost,
                    "min_cost": min_cost,
                    "max_cost": max_cost,
                    "mean_cost": mean_cost,
                    "total_profit": total_profit,
                    "min_profit": min_profit,
                    "max_profit": max_profit,
                    "mean_profit": mean_profit,
                    "total_marketing_cost": total_marketing_cost,
                    "min_marketing_cost": min_marketing_cost,
                    "max_marketing_cost": max_marketing_cost,
                    "mean_marketing_cost": mean_marketing_cost,
                    "profit_margin": profit_margin
                }
            
    return metrics