import pandas as pd
from app.utils.b64_to_bytes import b64_to_bytes
from io import BytesIO

def excel_to_bytes(base64_str: str) -> bytes:
    excel_file = b64_to_bytes(base64_str)
    if excel_file is None:
        return "Ko the giai ma file excel hoac file khong hop le."
    else:
        try:
            df = pd.read_excel(BytesIO(excel_file))
            return df.to_csv(index=False).encode('utf-8')
        except Exception as e:
            return e