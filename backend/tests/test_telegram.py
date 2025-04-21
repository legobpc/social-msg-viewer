import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from types import SimpleNamespace

from app.main import app
from app.auth_routes import get_current_user
from app.telegram.utils import get_user_client
from app.telegram_routes import session_data
import app.telegram.utils as tg_utils


@pytest.fixture
def fake_user():
    class FakeUser:
        id = 1
    return FakeUser()


@pytest.fixture
def fake_client():
    client = AsyncMock()
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    client.is_user_authorized = AsyncMock()
    client.send_code_request = AsyncMock(
        return_value=SimpleNamespace(phone_code_hash="fake_hash")
    )
    client.sign_in = AsyncMock(return_value=True)
    client.get_me = AsyncMock(return_value=AsyncMock(
        id=12345,
        username="testuser",
        first_name="Test",
        phone="+123456789"
    ))

    # Mocked chat entity
    dialog_entity = AsyncMock()
    dialog_entity.id = 111
    dialog_entity.title = "Chat Title"
    dialog_entity.username = "chatuser"
    client.get_dialogs = AsyncMock(return_value=[AsyncMock(entity=dialog_entity)])

    # Mocked message
    msg_mock = AsyncMock()
    msg_mock.id = 1
    msg_mock.text = "Hello"
    msg_mock.date = "2025-04-21T10:00:00"
    msg_mock.from_id = type("obj", (object,), {"user_id": 1})

    async def fake_iter_messages(*args, **kwargs):
        yield msg_mock

    client.get_entity = AsyncMock(return_value="chat_entity")
    client.iter_messages = fake_iter_messages
    client.log_out = AsyncMock()
    return client


@pytest.fixture(autouse=True)
def override_deps(fake_user, fake_client):
    # Override FastAPI dependencies and replace Telegram client
    app.dependency_overrides[get_current_user] = lambda: fake_user
    tg_utils.get_user_client = lambda user: fake_client
    yield fake_client
    # Reset after each test
    app.dependency_overrides.clear()
    tg_utils.get_user_client = get_user_client
    session_data.clear()


@pytest.mark.asyncio
async def test_connect(override_deps):
    override_deps.is_user_authorized = AsyncMock(return_value=False)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/connect")
    assert res.status_code == 200
    assert "Code sent" in res.json()["message"]


@pytest.mark.asyncio
async def test_login(override_deps):
    override_deps.is_user_authorized = AsyncMock(return_value=False)
    session_data[1] = "fake_hash"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/login?code=1234")
    assert res.status_code == 200
    assert res.json()["message"] == "Logged in"


@pytest.mark.asyncio
async def test_get_me(fake_client):
    fake_client.is_user_authorized = AsyncMock(return_value=True)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/me")
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_chats(override_deps):
    override_deps.is_user_authorized = AsyncMock(return_value=True)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/chats")
    assert res.status_code == 200
    assert res.json()[0]["title"] == "Chat Title"


@pytest.mark.asyncio
async def test_get_messages():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/messages?username=testchat")
    assert res.status_code == 200
    assert res.json()[0]["text"] == "Hello"


@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/logout")
    assert res.status_code == 200
    assert res.json()["message"] == "Logged out from Telegram"
