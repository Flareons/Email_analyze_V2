# Email_analyze
Analyze system for incoming email with Gemini 2.5 Flash

# Function
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

**client:**Google client class
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
