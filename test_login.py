from app import app
import pytest
import base64

test_client = app.test_client()

@pytest.mark.asyncio
async def test_get_login() -> None:
    response = await test_client.get("/login")
    data = await response.get_json()
    assert response.status_code == 200
    assert data == {"message": "Send based64(username:password) in Authorization header"}

@pytest.mark.asyncio
async def test_post_login_success() -> None:
    valid_credentials = base64.b64encode(b"testusername:testpassword").decode("utf-8")
    response = await test_client.post(
        "/login",
        headers={"Authorization": "Basic " + valid_credentials}
    )
    data = await response.get_json()
    assert response.status_code == 200
    assert data == {"authenticated": True}

@pytest.mark.asyncio
async def test_post_login_success() -> None:
    valid_credentials = base64.b64encode(b"testusername:testpassword").decode("utf-8")
    response = await test_client.post(
        "/login",
        headers={"Authorization": "Basic " + valid_credentials}
    )
    data = await response.get_json()
    assert response.status_code == 200
    assert data == {"authenticated": True}

@pytest.mark.asyncio
async def test_post_login_missing_credentials() -> None:
    response = await test_client.post("/login")
    data = await response.get_json()
    assert "WWW-Authenticate" in response.headers 
    assert response.headers["WWW-Authenticate"] == "Basic"
    assert response.status_code == 401
    assert data == {
    "message": "Invalid/ Missing username or password. Send based64(username:password) in Authorization header"}

@pytest.mark.asyncio
async def test_post_login_invalid_credentials() -> None:
    invalid_credentials = base64.b64encode(b"wrongusername:wrongpassword").decode("utf-8")
    response = await test_client.post(
        "/login",
        headers={"Authorization": "Basic " + invalid_credentials}
    )
    data = await response.get_json()
    assert "WWW-Authenticate" in response.headers 
    assert response.headers["WWW-Authenticate"] == "Basic"
    assert response.status_code == 401
    assert data == {
    "message": "Invalid/ Missing username or password. Send based64(username:password) in Authorization header"}