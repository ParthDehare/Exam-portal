import pytest

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post(
        "/api/auth/register",
        json={
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "role": "candidate"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_user(async_client):
    user_data = {
        "fullname": "Test User 2",
        "email": "test2@example.com",
        "password": "StrongPassword123!",
        "role": "candidate"
    }
    await async_client.post("/api/auth/register", json=user_data)
    response = await async_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(async_client):
    user_data = {
        "fullname": "Login Test User",
        "email": "logintest@example.com",
        "password": "StrongPassword123!",
        "role": "candidate"
    }
    await async_client.post("/api/auth/register", json=user_data)
    
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "StrongPassword123!"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    # Check that HTTPOnly cookie was set
    assert "access_token" in response.cookies

@pytest.mark.asyncio
async def test_login_invalid_password(async_client):
    user_data = {
        "fullname": "Login Test User",
        "email": "logintest2@example.com",
        "password": "StrongPassword123!",
        "role": "candidate"
    }
    await async_client.post("/api/auth/register", json=user_data)
    
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "logintest2@example.com",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
