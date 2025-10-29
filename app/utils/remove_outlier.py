import pandas as pd

def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    # Lấy các cột số
    df_num = df.select_dtypes(include=['number'])
    
    # Tính IQR cho các cột số
    Q1 = df_num.quantile(0.25)
    Q3 = df_num.quantile(0.75)
    IQR = Q3 - Q1

    # Tạo mask các dòng không có outlier
    mask = ~((df_num < (Q1 - 1.5 * IQR)) | (df_num > (Q3 + 1.5 * IQR))).any(axis=1)
    
    # Áp dụng mask lên toàn bộ df (bao gồm cả cột string)
    return df[mask].reset_index(drop=True)