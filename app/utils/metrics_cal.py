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

    print(sorted(target_periods))

    # Lọc dữ liệu dựa trên các khoảng thời gian đã trích xuất
    filtered_df = df_dup[df_dup["YearMonth"].isin(target_periods)]

    # Gộp dữ liệu theo YearMonth để tính toán các metrics
    grouped = filtered_df.groupby("YearMonth")

    # Tính toán các metrics theo ý định của người dùng
    
    # Tính theo tổng thể theo thời gian
    if date_info.intent == "Tổng thể":
        for date, df_fil in grouped:
            print(date)
            #Chỉ số của doanh thu
            total_revenue = df_fil["Revenue"].sum()

            #Chỉ số về chi phí
            total_product_cost = df_fil["Cost"].sum()
            total_marketing_cost = df_fil["Marketing_Cost"].sum()
            total_discount = df_fil["Discount"].sum()
            total_cost = total_marketing_cost + total_product_cost +total_discount

            #Chỉ số về lợi nhuận
            total_profit = df_fil["Profit"].sum()
            profit_margin = ((total_profit + total_marketing_cost) / total_revenue * 100) if total_revenue != 0 else 0

            #Chỉ số kênh bán hàng
            online_order_rate = int(df_fil[df_fil["Channel"] == "Online"].shape[0]) / int(df_fil["Channel"].shape[0])
            offline_order_rate = int(df_fil[df_fil["Channel"] == "Offline"].shape[0]) / int(df_fil["Channel"].shape[0])
            
            #Chỉ số kênh thanh toán
            card_rate = int(df_fil[df_fil["Payment_Method"] == "Card"].shape[0]) / int(df_fil["Payment_Method"].shape[0])
            e_wallet_rate = int(df_fil[df_fil["Payment_Method"] == "E-wallet"].shape[0]) / int(df_fil["Payment_Method"].shape[0])
            cash_rate = int(df_fil[df_fil["Payment_Method"] == "Cash"].shape[0]) / int(df_fil["Payment_Method"].shape[0])

            #Chỉ số khách hàng
            customer_count = len(df_fil["Customer_ID"].unique())

            metrics[str(date)] = {
                "total_revenue": float(total_revenue),
                "total_product_cost": float(total_product_cost),
                "total_marketing_cost": float(total_marketing_cost),
                "total_discount": float(total_discount),
                "total_cost": float(total_cost),
                "total_profit": float(total_profit),
                "profit_margin": float(profit_margin),
                "online_order_rate": float(online_order_rate),
                "offline_order_rate": float(offline_order_rate),
                "card_rate": float(card_rate),
                "e_wallet_rate": float(e_wallet_rate),
                "cash_rate": float(cash_rate),
                "customer_count": int(customer_count)                
            }
    
    #Tính theo từng sản phẩm theo thời gian
    elif date_info.intent == "Theo sản phẩm":
        for date, df_fil in grouped:
            product = df["Product_Category"].unique()
            metrics[str(date)] = {}

            for p in product:
                df_prod = df_fil[df_fil["Product_Category"] == p]
                
                #Chỉ số doanh thu của sản phẩm
                total_revenue = df_prod["Revenue"].sum()

                #Chỉ số chi phí của sản phẩm
                total_product_cost = df_prod["Cost"].sum()
                total_marketing_cost = df_prod["Marketing_Cost"].sum()
                total_discount = df_prod["Discount"].sum()
                total_cost = total_marketing_cost + total_product_cost + total_discount

                #Chỉ số lợi nhuận của sản phẩm
                total_profit = df_prod["Profit"].sum()
                profit_margin = ((total_profit + total_marketing_cost) / total_revenue * 100) if total_revenue != 0 else 0

                #Chỉ số kênh bán hàng
                online_order_rate = int(df_prod[df_prod["Channel"] == "Online"].shape[0]) / int(df_prod["Channel"].shape[0])
                offline_order_rate = int(df_prod[df_prod["Channel"] == "Offline"].shape[0]) / int(df_prod["Channel"].shape[0])
                
                #Chỉ số kênh thanh toán
                card_rate = int(df_prod[df_prod["Payment_Method"] == "Card"].shape[0]) / int(df_prod["Payment_Method"].shape[0])
                e_wallet_rate = int(df_prod[df_prod["Payment_Method"] == "E-wallet"].shape[0]) / int(df_prod["Payment_Method"].shape[0])
                cash_rate = int(df_prod[df_prod["Payment_Method"] == "Cash"].shape[0]) / int(df_prod["Payment_Method"].shape[0])

                #Chỉ số lượng bán ra
                total_quantity = df_prod["Quantity"].sum()

                #Chỉ số khách hàng
                customer_count = len(df_prod["Customer_ID"].unique())

                metrics[str(date)][p] = {
                    "total_revenue": float(total_revenue),
                    "total_product_cost": float(total_product_cost),
                    "total_marketing_cost": float(total_marketing_cost),
                    "total_discount": float(total_discount),
                    "total_cost": float(total_cost),
                    "total_profit": float(total_profit),
                    "profit_margin": float(profit_margin),
                    "online_order_rate": float(online_order_rate),
                    "offline_order_rate": float(offline_order_rate),
                    "card_rate": float(card_rate),
                    "e_wallet_rate": float(e_wallet_rate),
                    "cash_rate": float(cash_rate),
                    "total_quantity": int(total_quantity),
                    "customer_count": int(customer_count)
                }
            
    return metrics