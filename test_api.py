import requests

def test_roi():
    assert requests.get("http://localhost:8000/roi").status_code == 200
