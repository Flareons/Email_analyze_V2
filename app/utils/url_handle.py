import requests

def url_to_bytes(url, timeout=10):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    # kiểm tra content-type (tuỳ ý)
    if 'image' not in resp.headers.get('Content-Type', ''):
        raise ValueError('URL không trả về image')
    return resp.content, resp.headers.get('Content-Type', 'application/octet-stream')

