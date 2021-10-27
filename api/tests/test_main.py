import pytest 

from main import app 
from fastapi.testclient import TestClient

@pytest.fixture
def testclient():
    return TestClient(app)

def test_healthz_post(testclient):
    response = testclient.post("/healthz")
    assert response.status_code == 405
    assert response.json() == {'detail': 'Method Not Allowed'}

def test_healthz(testclient):
    response = testclient.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

def test_api_wrong_request(testclient):
    response = testclient.get("/api/v1/voucher")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

def test_api_request_missing_fields(testclient):
    response = testclient.post(
        "/api/v1/voucher", 
        headers={"Content-Type": "application/json"},
        json={"wrong": "missing"}
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': 
            [{'loc': ['body', 'customer_id'],
            'msg': 'field required',
            'type': 'value_error.missing'},
            {'loc': ['body', 'country_code'],
            'msg': 'field required',
            'type': 'value_error.missing'},
            {'loc': ['body', 'last_order_ts'],
            'msg': 'field required',
            'type': 'value_error.missing'},
            {'loc': ['body', 'first_order_ts'],
            'msg': 'field required',
            'type': 'value_error.missing'},
            {'loc': ['body', 'total_orders'],
            'msg': 'field required',
            'type': 'value_error.missing'},
            {'loc': ['body', 'segment_name'],
        'msg': 'field required',
        'type': 'value_error.missing'}]
    }

def test_api_request_validation_country(testclient):
    response = testclient.post(
        "/api/v1/voucher", 
        headers={"Content-Type": "application/json"},
        json={
            "customer_id": 123, 
            "country_code": "China",
            "last_order_ts": "2021-10-26 00:00:00",
            "first_order_ts": "2021-10-26 00:00:00",
            "total_orders": 14,
            "segment_name": "frequent_segment"
        }
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{'loc': ['body', 'country_code'],
        'msg': 'this API is only concerned with vouchers for Peru',
        'type': 'value_error'}]
    }

def test_api_request_validation_segment(testclient):
    response = testclient.post(
        "/api/v1/voucher", 
        headers={"Content-Type": "application/json"},
        json={
            "customer_id": 123, 
            "country_code": "Peru",
            "last_order_ts": "2021-10-26 00:00:00",
            "first_order_ts": "2021-10-26 00:00:00",
            "total_orders": 14,
            "segment_name": "missing_segment"
        }
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{'loc': ['body', 'segment_name'],
        'msg': "segment_name: missing_segment not understood -- only 'frequent_segment' and 'recency_segment' allowed",
        'type': 'value_error'}]
    }

def test_api_request_valid_frequent(testclient):
    response = testclient.post(
        "/api/v1/voucher", 
        headers={"Content-Type": "application/json"},
        json={
            "customer_id": 123, 
            "country_code": "Peru",
            "last_order_ts": "2021-10-26 00:00:00",
            "first_order_ts": "2021-10-26 00:00:00",
            "total_orders": 14,
            "segment_name": "frequent_segment"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json()['voucher'], int)

def test_api_request_valid_recency(testclient):
    response = testclient.post(
        "/api/v1/voucher", 
        headers={"Content-Type": "application/json"},
        json={
            "customer_id": 123, 
            "country_code": "Peru",
            "last_order_ts": "2021-09-14 00:00:00",
            "first_order_ts": "2021-10-26 00:00:00",
            "total_orders": 14,
            "segment_name": "recency_segment"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json()['voucher'], int)
