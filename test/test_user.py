from app import app
import pytest
import base64

test_client = app.test_client()

@pytest.mark.asyncio
async def test_home() -> None:
    response = await test_client.get("/")
    data = await response.get_json()
    assert response.status_code == 200
    assert data == {"message": "Welcome to wordle!"}

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

@pytest.mark.asyncio
async def test_get_register() -> None:
    response = await test_client.get("/register")
    data = await response.get_json()
    assert response.status_code == 200
    assert data == {"message": "Pass in username and password in POST request"}

@pytest.mark.asyncio
async def test_post_register_success() -> None:
    newUser = {"username": "newusername", "password": "newpassword"}
    response = await test_client.post("/register", json=newUser)
    data = await response.get_json()
    assert response.status_code == 200
    assert data == {"message": "User registered"}

@pytest.mark.asyncio
async def test_post_register_no_data() -> None:
    response = await test_client.post("/register")
    data = await response.get_json()
    assert response.status_code == 400
    assert data == {"message": "Required username and password"}

@pytest.mark.asyncio
async def test_post_register_missing_password() -> None:
    newUser = {"username": "newUsername"}
    response = await test_client.post("/register", json=newUser)
    data = await response.get_json()
    assert response.status_code == 400
    assert data == {"message": "Required username and password"}

@pytest.mark.asyncio
async def test_post_register_missing_username() -> None:
    newUser = {"password": "newPassword"}
    response = await test_client.post("/register", json=newUser)
    data = await response.get_json()
    assert response.status_code == 400
    assert data == {"message": "Required username and password"}

@pytest.mark.asyncio
async def test_post_register_unavailable_username() -> None:
    newUser = {"username": "testusername", "password": "testpassword"}
    response = await test_client.post("/register", json=newUser)
    data = await response.get_json()
    assert response.status_code == 400
    assert data == {"message": "Username not availabe"}