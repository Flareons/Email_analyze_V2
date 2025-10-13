import pytest
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pydantic import ValidationError
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.routes.email_intent_finder import EmailItems

TEST_CASES_FILE = os.path.join(os.path.dirname(__file__), "test_case.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")

@pytest.fixture(scope="session")
def client():
    """Tạo TestClient (chạy 1 lần cho toàn bộ session pytest)."""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def test_cases():
    """Đọc test cases từ file JSON."""
    if not os.path.exists(TEST_CASES_FILE):
        pytest.skip(f"Không tìm thấy file test cases: {TEST_CASES_FILE}")
    with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)
    return cases

def save_results(results, path=RESULTS_FILE):
    """Ghi kết quả ra file JSON (ghi đè mỗi lần chạy)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "results": results
        }, f, ensure_ascii=False, indent=2)

def prepare_request(case):
    """Chuẩn hóa request info từ case."""
    method = case.get("method", "POST").upper()
    path = case["path"]
    params = case.get("params")  # dict or None
    json_body = case.get("json")
    headers = case.get("headers") or {}
    data = case.get("data")  # form data if any
    return method, path, params, json_body, headers, data

def run_case(client, case):
    """Thực hiện 1 case, trả về dict kết quả."""
    name = case.get("name") or case.get("path")
    method, path, params, json_body, headers, data = prepare_request(case)

    result = {
        "name": name,
        "path": path,
        "method": method,
        "expected_status": case.get("expected_status"),
        "validation_ok": False,
        "ok": False,
        "status_code": None,
        "response": None,
        "error": None,
        "passed_status_check": False
    }

    # 1) Validate input JSON theo EmailRequest
    payload = json_body or {}
    EmailItems(**payload)
    result["validation_ok"] = True

    # 2) Gọi API
    try:
        if method == "GET":
            resp = client.get(path, params=params, headers=headers)
        elif method == "POST":
            if json_body is not None:
                resp = client.post(path, json=json_body, headers=headers, params=params)
            else:
                resp = client.post(path, data=data, headers=headers, params=params)
        elif method == "PUT":
            if json_body is not None:
                resp = client.put(path, json=json_body, headers=headers, params=params)
            else:
                resp = client.put(path, data=data, headers=headers, params=params)
        elif method == "DELETE":
            resp = client.delete(path, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        result["status_code"] = resp.status_code
        # cố gắng parse JSON, fallback sang text
        try:
            result["response"] = resp.json()
        except Exception:
            result["response"] = resp.text

        # check expected status
        exp_status = case.get("expected_status")
        if exp_status is not None:
            status_ok = (resp.status_code == exp_status)
        else:
            status_ok = (200 <= resp.status_code < 300)

        result["passed_status_check"] = status_ok

        # nếu có expected_response, so sánh strict equality (bạn có thể thay đổi logic)
        exp_resp = case.get("expected_response")
        if exp_resp is not None:
            resp_ok = (result["response"] == exp_resp)
        else:
            resp_ok = True

        result["ok"] = status_ok and resp_ok

    except Exception as e:
        result["error"] = str(e)

    return result

def test_run_all_cases(client: TestClient, test_cases:json):
    """Chạy tất cả case, lưu results, và fail pytest nếu có case fail."""
    results = []
    any_failed = False
    for case in test_cases:
        r = run_case(client, case)
        results.append(r)
        if not (r.get("validation_ok") and r.get("ok")):
            any_failed = True

    save_results(results)

    # Nếu muốn pytest fail khi có case không pass, giữ assert dưới.
    assert not any_failed, f"Có {sum(1 for r in results if not (r.get('validation_ok') and r.get('ok')))} test case failed. Xem {RESULTS_FILE} để biết chi tiết."