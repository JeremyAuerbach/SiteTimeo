from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.auth import COOKIE_NAME, purge_expired
from app.models import AuthSession, User


def register(client, username="timeo", password="motdepasse"):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def test_register_connects_the_user(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json()["username"] == "timeo"
    assert response.json()["is_guest"] is False

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "timeo"


def test_register_rejects_taken_username_case_insensitively(client):
    register(client)
    response = register(client, username="TIMEO")
    assert response.status_code == 409


def test_register_validates_input(client):
    assert register(client, username="ab").status_code == 422
    assert register(client, username="pas d'espace").status_code == 422
    assert register(client, password="court").status_code == 422


def test_login(client):
    register(client)
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401

    bad = client.post("/api/auth/login", json={"username": "timeo", "password": "mauvais!!"})
    assert bad.status_code == 401
    unknown = client.post("/api/auth/login", json={"username": "inconnu", "password": "x"})
    assert unknown.status_code == 401

    ok = client.post("/api/auth/login", json={"username": "Timeo", "password": "motdepasse"})
    assert ok.status_code == 200
    assert client.get("/api/auth/me").json()["username"] == "timeo"


def test_guest_cannot_be_logged_into_with_a_password(client):
    client.post("/api/auth/guest", json={"username": "visiteur"})
    client.cookies.clear()
    response = client.post("/api/auth/login", json={"username": "visiteur", "password": ""})
    assert response.status_code == 401


def test_guest_session_and_logout_deletes_account(client, session_factory):
    response = client.post("/api/auth/guest", json={"username": "visiteur"})
    assert response.status_code == 201
    assert response.json()["is_guest"] is True
    assert "max-age" not in response.headers["set-cookie"].lower()

    assert client.get("/api/auth/me").json()["username"] == "visiteur"
    assert client.post("/api/auth/logout").status_code == 204

    with session_factory() as db:
        assert db.scalar(select(User).where(User.username == "visiteur")) is None
    # Le pseudo est de nouveau libre.
    assert client.post("/api/auth/guest", json={"username": "visiteur"}).status_code == 201


def test_guest_username_cannot_steal_existing_account(client):
    register(client)
    client.cookies.clear()
    assert client.post("/api/auth/guest", json={"username": "timeo"}).status_code == 409


def test_purge_removes_inactive_guests_and_expired_sessions(client, session_factory):
    register(client)
    client.cookies.clear()
    client.post("/api/auth/guest", json={"username": "visiteur"})

    past = datetime.now(UTC) - timedelta(minutes=1)
    with session_factory() as db:
        db.execute(update(AuthSession).values(expires_at=past))
        db.commit()

    assert client.get("/api/auth/me").status_code == 401

    with session_factory() as db:
        purge_expired(db)
        usernames = set(db.scalars(select(User.username)))
        assert usernames == {"timeo"}
        assert db.scalars(select(AuthSession)).all() == []


def test_me_without_cookie(client):
    assert client.get("/api/auth/me").status_code == 401
    client.cookies.set(COOKIE_NAME, "jeton-invalide")
    assert client.get("/api/auth/me").status_code == 401
