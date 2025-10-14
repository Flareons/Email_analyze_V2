# Email_analyze
Analyze system for incoming email

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
**client:**Google client class
```python
client = genai.Client(api_key=gemini_api_key)
```

- **Output:**
Json of sumary, intent and attachement_analyze
```python
{
    "intent": "str"
    "sumarize": "str"
    "attachments": "list[str]"
}
```
