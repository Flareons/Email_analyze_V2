# Email_analyze
Analyze system for incoming email with Gemini 2.5 Flash with MySQL database

# Main function
### analyze(e, client)
- **Input:**<br>
**e:** Detail email
```python
[
    {
        "email": "Details email",
        "attachments": [
            {
                "mime_type": "attachment data type",
                "b64_str": "encoded base64 string data"
            }
        ]
    }
]
```
<br>

**client:** Google client class
```python
client = genai.Client(api_key=gemini_api_key)
```

- **Output:**
Json of sumary, intent, attachments analysis and token count
```python
{
    "intent": "str"
    "sumarize": "str"
    "attachments": "list[str]"
},
prompt_token,
generate_token,
thoughts_token
```

# API module
### email_intent_finder.py

Module này chứa API trích xuất thông tin chính của email bao gồm: "Ý định của người dùng **intent**", "Tóm tắt **sumarize**" và "Phân tích tệp đính kèm **attachments**". Bằng cách gọi đến mô hình Gemini thông qua hàm **analyze(e, client)**<br>

- **Prefix:** **/email_intent_finder/email**

- **Base model:** 
```python
class EmailRequest(BaseModel):
    email: Optional[str] = None
    attachment: Optional[List[Dict]] = None

class EmailItems(BaseModel):
    items: List[EmailRequest]
```

- **Method**: POST

- **Input:**
```python
    analyze_email(req: EmailItems, request: Request, Session: SessionDep)
```
<br>

**req:EmailItems:** request đầu vào phải chứa một json thỏa mãn điều kiện của **EmailItem**
```python
[
    {
        'email': "Nội dung email"
        'attachment': [
            # Nếu là đính kèm ảnh
            {
                'mime_type': "Kiểu dữ liệu của tệp đính kèm"
                'base_64_str': "Ảnh qua mail thường để dạng base 64 string"
            }
            # Nếu là đính kèm link
            {
                'mime_type': "url",
                'link': "link đính kèm"
            }
        ] 
    }
]
```

**request: Request:** chứa các request HTTPS và cả thông tin khởi tạo lifespan của ứng dụng FastAPI.<br>

**Session:SessionDep:** Session annotation của database để sử dụng trong các route.<br>

- **Output:** Trả về list chứa thông tin phân tích của email gửi tới và lượng token sử dụng<br>
```python
[
    {
        'response': {
            'intent': str,
            'sumarize': str,
            'attachments': str
        },
        "prompt_token": "Số token của prompt",
        "generate_token": "Số token của câu trả lời",
        "thought_token": "Số token sử dụng để thingking"
    }
]
```

# Tùy chỉnh:
Thêm file **.env** chứa các trường sau đây:<br>
**GENAI_API_KEY:** API key của gemini<br>
**DB_USERNAME:** Tên tài khoản truy của database<br>
**DB_PASSWORD:** Password để truy cập database<br>
**DB_HOST:** Địa chỉ host của database<br>
**DB_PORT:** Cổng Port của database<br>
**DB_NAME:** Tên của database<br>

# Cách test:
**Cài các thư viện của repo:**
```cmd
pip install -r requirements.txt
```

- **Test với Postman:**
<br>
Thêm file .env rồi chạy sever với uvicorn và đưa thông tin vào API với cấu trúc json đã cung cấp ở phần API bên trên<br>
```bash
uvicorn app.main:app --reload 
```

- **Unit test:**
<br>
Thêm file .env và chạy thư viện pytest
<br>
```bash
pytest app/test/test_api_email.py
```
<br>
Kết quả test sẽ ở file results.json<br>