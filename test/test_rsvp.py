# from main import seed
# from db.connection import get_connection
# from main import app
# from fastapi.testclient import TestClient

# def test_authorised_user_can_rsvp_an_event(client):
#     login_response = client.post(
#         "/api/login",
#         json={
#             "email": "alice@example.com",
#             "password": "password123"
#         }
#     )

#     token = login_response.json()["token"]

#     response = client.post(
#         "/api/events/1/rsvp",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     assert response.status_code == 409


from main import create_app, seed
from db.connection import get_connection
from fastapi.testclient import TestClient


def test_authenticated_user_can_rsvp_an_event():
    # ✅ Seed DB first
    conn = get_connection()
    seed(conn)
    conn.close()

    # ✅ Create a fresh app instance for this test
    app = create_app()

    # ✅ Use TestClient context manager (ensures startup/shutdown run)
    with TestClient(app) as client:

        login_response = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = client.post(
            "/api/events/1/rsvp",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        

def test_rsvp_without_token_returns_401():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:

        response = client.post("/api/events/1/rsvp")

        assert response.status_code == 401


def test_non_existent_event_returns_404():

    # ✅ Seed DB first
    conn = get_connection()
    seed(conn)
    conn.close()

    # ✅ Create a fresh app instance for this test
    app = create_app()

    # ✅ Use TestClient context manager (ensures startup/shutdown run)
    with TestClient(app) as client:

        login_response = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = client.post(
            "/api/events/9999/rsvp",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_duplicate_rsvp_on_event_returns_409():

    # ✅ Seed DB first
    conn = get_connection()
    seed(conn)
    conn.close()

    # ✅ Create a fresh app instance for this test
    app = create_app()

    # ✅ Use TestClient context manager (ensures startup/shutdown run)
    with TestClient(app) as client:

        login_response = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = client.post(
            "/api/events/1/rsvp",
            headers={"Authorization": f"Bearer {token}"}
        )



        response = client.post(
            "/api/events/1/rsvp",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 409



def test_delete_rsvp_without_token_returns_401():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:

        response = client.delete("/api/events/events/1/rsvp/me")

        assert response.status_code == 401


def test_deleting_rsvp_without_creating_first_returns_404():
    # ✅ Seed DB first
    conn = get_connection()
    seed(conn)
    conn.close()

    # ✅ Create a fresh app instance for this test
    app = create_app()

    # ✅ Use TestClient context manager (ensures startup/shutdown run)
    with TestClient(app) as client:

        login_response = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )

        token = login_response.json()["access_token"]

        response = client.delete(
            "/api/events/1/rsvp/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        

        assert response.status_code == 404


