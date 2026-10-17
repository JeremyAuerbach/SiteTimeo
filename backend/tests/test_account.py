from sqlalchemy import select

from app.models import AuthSession, UserAvatar

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 32


def register(client, username="timeo", password="motdepasse"):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def test_change_username(client):
    register(client)
    response = client.patch("/api/account", json={"username": "Timeo_2"})
    assert response.status_code == 200
    assert response.json()["username"] == "Timeo_2"
    assert client.get("/api/auth/me").json()["username"] == "Timeo_2"


def test_change_username_case_of_own_name(client):
    register(client)
    assert client.patch("/api/account", json={"username": "TIMEO"}).status_code == 200


def test_change_username_rejects_taken_or_invalid(client):
    register(client, username="autre")
    client.cookies.clear()
    register(client)
    assert client.patch("/api/account", json={"username": "Autre"}).status_code == 409
    assert client.patch("/api/account", json={"username": "ab"}).status_code == 422


def test_guest_can_change_username(client):
    client.post("/api/auth/guest", json={"username": "visiteur"})
    response = client.patch("/api/account", json={"username": "visiteur2"})
    assert response.status_code == 200


def test_change_password(client, session_factory):
    register(client)
    # Deuxième appareil connecté au même compte.
    other = client.__class__(client.app)
    other.post("/api/auth/login", json={"username": "timeo", "password": "motdepasse"})

    wrong = client.put(
        "/api/account/password",
        json={"current_password": "mauvais!!", "new_password": "nouveau-mdp"},
    )
    assert wrong.status_code == 400
    too_short = client.put(
        "/api/account/password",
        json={"current_password": "motdepasse", "new_password": "court"},
    )
    assert too_short.status_code == 422

    ok = client.put(
        "/api/account/password",
        json={"current_password": "motdepasse", "new_password": "nouveau-mdp"},
    )
    assert ok.status_code == 204
    # Cet appareil reste connecté, l'autre est déconnecté.
    assert client.get("/api/auth/me").status_code == 200
    assert other.get("/api/auth/me").status_code == 401
    with session_factory() as db:
        assert len(db.scalars(select(AuthSession)).all()) == 1

    client.post("/api/auth/logout")
    old = client.post("/api/auth/login", json={"username": "timeo", "password": "motdepasse"})
    assert old.status_code == 401
    new = client.post("/api/auth/login", json={"username": "timeo", "password": "nouveau-mdp"})
    assert new.status_code == 200


def test_guest_has_no_password_to_change(client):
    client.post("/api/auth/guest", json={"username": "visiteur"})
    response = client.put(
        "/api/account/password", json={"current_password": "", "new_password": "nouveau-mdp"}
    )
    assert response.status_code == 403


def test_avatar_upload_replace_and_delete(client):
    user = register(client).json()
    assert user["avatar_url"] is None

    response = client.put("/api/account/avatar", content=PNG)
    assert response.status_code == 200
    url = response.json()["avatar_url"]
    assert url.startswith(f"/api/users/{user['id']}/avatar")
    assert client.get("/api/auth/me").json()["avatar_url"] == url

    image = client.get(url)
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content == PNG

    replaced = client.put("/api/account/avatar", content=WEBP)
    assert replaced.status_code == 200
    assert client.get(replaced.json()["avatar_url"]).headers["content-type"] == "image/webp"

    deleted = client.delete("/api/account/avatar")
    assert deleted.json()["avatar_url"] is None
    assert client.get(url).status_code == 404


def test_avatar_rejects_non_images_and_large_files(client):
    register(client)
    assert client.put("/api/account/avatar", content=b"<svg></svg>").status_code == 415
    big = PNG + b"\x00" * (2 * 1024 * 1024)
    assert client.put("/api/account/avatar", content=big).status_code == 413


def test_avatar_deleted_with_guest(client, session_factory):
    client.post("/api/auth/guest", json={"username": "visiteur"})
    client.put("/api/account/avatar", content=PNG)
    client.post("/api/auth/logout")
    with session_factory() as db:
        assert db.scalars(select(UserAvatar)).all() == []


def test_avatar_requires_login(client):
    assert client.put("/api/account/avatar", content=PNG).status_code == 401
    assert client.get("/api/users/1/avatar").status_code == 401
