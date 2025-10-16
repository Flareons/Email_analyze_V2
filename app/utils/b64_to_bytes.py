import base64

def b64_to_bytes(b64_string):
    if "," in b64_string:
        _, b64_string = b64_string.split(",", 1)

    # decode base64 -> bytes
    try:
        img_bytes = base64.b64decode(b64_string)
    except Exception:
        # Nếu decode thất bại, bỏ file đó qua (giữ logic: không dừng toàn bộ request)
        return None
    return img_bytes