
from main import seed, app
from db.connection import get_connection
from main import create_app
from fastapi.testclient import TestClient




def test_events_table_resets_on_seed():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()

   
    cur.execute("""
        INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        "FAKE EVENT",
        "Should disappear",
        "2026-01-01 10:00:00",
        "2026-01-01 12:00:00",
        1,
        1
    ))
    conn.commit()



    cur.execute("SELECT COUNT(*) FROM events;")
    count_with_fake = cur.fetchone()[0]


    seed(conn)

    cur.execute("SELECT COUNT(*) FROM events;")
    count_after_seed = cur.fetchone()[0]


    assert count_after_seed < count_with_fake

    cur.close()
    conn.close()


def test_all_data_is_inserted_into_table():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events;")
    count_rows = cur.fetchone()[0]

    assert count_rows == 10

    cur.close()
    conn.close()
    

def test_seed_is_idempotent_for_events():
    conn = get_connection()
    seed(conn)
    seed(conn)
    seed(conn)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events;")
    count = cur.fetchone()[0]

    assert count == 10

    cur.close()
    conn.close()


def test_specific_record_in_table_exists():
    

    conn = get_connection()
    seed(conn)
    cur = conn.cursor()
    cur.execute("""
        SELECT title FROM events
        WHERE title = %s;
        """, ("Leeds Tech Meetup – June Edition",))

    result = cur.fetchone()

    assert result is not None
    cur.close()
    conn.close()

#### test endpoints ##




# def test_events_returns_all():
#     conn = get_connection()
#     seed(conn)
#     conn.cursor()
#     with TestClient(app) as client:
#         response = client.get("/events")
#     assert response.status_code == 200

#     body = response.json()

#     assert isinstance(body, list)
#     assert len(body) == 10

#     for event in body:
#         assert isinstance(event["id"], int)
#         assert isinstance(event["title"], str)
#         assert event["description"] is None or isinstance(event["description"], str)
#         assert isinstance(event["starts_at"], str)
#         assert isinstance(event["ends_at"], str)
#         assert isinstance(event["organiser_id"], int)
#         assert isinstance(event["venue_id"], int)
#         assert isinstance(event["created_at"], str)




def test_events_returns_all():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:
        response = client.get("/events")
        assert response.status_code == 200

def test_events_returns_by_id():
    conn = get_connection()
    seed(conn)
    conn.close()
    with TestClient(app) as client:
        response = client.get("/events/1")
        assert response.status_code == 200
        response = client.get("/events/999999")
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "NOT_FOUND"
        assert response.json()["detail"]["message"] == "Route not found" 
        body = response.json()

        assert isinstance(body, dict)
        assert len(body) == 1




def test_authorised_user_can_create_an_event():
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

        response = client.post(
            "/api/events",
            headers={"Authorization": f"Bearer {token}"},
            json={
                    "title": "Summer Rooftop Social",
                    "description": "An evening of networking and good vibes.",
                    "starts_at": "2025-08-15T18:00:00Z",
                    "ends_at": "2025-08-15T21:00:00Z",
                    "venue_id": 2
                 }
        )

        
        body = response.json()

        # ✅ Check structure
        assert isinstance(body, dict)
        assert "event" in body

        event = body["event"]

        # ✅ Check fields exist
        assert set(event.keys()) == {
            "id",
            "title",
            "description",
            "starts_at",
            "ends_at",
            "venue_id",
            "organiser_id",
            "created_at"
        }


        assert response.status_code == 201


def test_missing_field_returns_400():
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

        response = client.post(
            "/api/events",
            headers={"Authorization": f"Bearer {token}"},
            json={  "title": "Summer Rooftop Social",
                    "description": "An evening of networking and good vibes.",
                    "starts_at": "2025-08-15T18:00:00Z",
                    "ends_at": "",
                    "venue_id": 2
                 }
        )

        



        assert response.status_code == 400

def test_invalid_token_for_creating_new_event_returns_401():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/events",
            headers={"Authorization": "Bearer invalidtoken"},
            json={
                "title": "Summer Rooftop Social",
                "description": "An evening of networking and good vibes.",
                "starts_at": "2025-08-15T18:00:00Z",
                "ends_at": "2025-08-15T21:00:00Z",
                "venue_id": 2
            }
        )

        assert response.status_code == 401


def test_non_existent_event_id_returns_404():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )

        token = login_response.json()["access_token"]

        response = client.patch(
            "/api/events/9999",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "description": "Updated description",
                "starts_at": "2025-08-16T19:00:00Z",
                "ends_at": "2025-08-16T23:00:00Z"
            }
        )

        assert response.status_code == 404


def test_invalid_date_format_returns_422():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )

        token = login_response.json()["access_token"]

        create_response = client.post(
            "/api/events",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test Event",
                "description": "Valid event",
                "starts_at": "2025-08-15T18:00:00Z",
                "ends_at": "2025-08-15T21:00:00Z",
                "venue_id": 2
            }
        )

        assert create_response.status_code == 201

        event_id = create_response.json()["event"]["id"]

        response = client.patch(
            f"/api/events/{event_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "ends_at": "2025-08-16T23"  # Invalid ISO format
            }
        )

        assert response.status_code == 400


def test_non_organiser_cannot_update_event_returns_403():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:

        # Login as Alice (organiser)
        alice_login = client.post(
            "/auth/login",
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
        )
        alice_token = alice_login.json()["access_token"]

        # Alice creates event
        create_response = client.post(
            "/api/events",
            headers={"Authorization": f"Bearer {alice_token}"},
            json={
                "title": "Test Event",
                "description": "Valid event",
                "starts_at": "2025-08-15T18:00:00Z",
                "ends_at": "2025-08-15T21:00:00Z",
                "venue_id": 2
            }
        )

        assert create_response.status_code == 201

        event_id = create_response.json()["event"]["id"]

        # Login as Bob (not organiser)
        bob_login = client.post(
            "/auth/login",
            json={
                "email": "bob@example.com",
                "password": "password123"
            }
        )
        bob_token = bob_login.json()["access_token"]

        # Bob attempts update
        response = client.patch(
            f"/api/events/{event_id}",
            headers={"Authorization": f"Bearer {bob_token}"},
            json={
                "description": "Hacked by Bob"
            }
        )

        assert response.status_code == 403



       


def test_get_attendee_list_for_authenticated_organiser_id():
    conn = get_connection()
    seed(conn)
    conn.close()
    app = create_app()

    with TestClient(app) as client:
            login_response =  client.post(
            "/auth/login",
            
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
            )
            token = login_response.json()["access_token"]
        
            response =  client.get(
            "/api/events/1/attendees",
        
            headers={"Authorization": f"Bearer {token}"}
            )
            
          
 
            assert response.status_code == 200
            data= response.json()
            assert "attendees" in data



def test_get_attendee_list_for_non_organiser_returns_403():
    conn = get_connection()
    seed(conn)
    conn.close()
    app = create_app()

    with TestClient(app) as client:
            login_response =  client.post(
            "/auth/login",
            
            json={
                "email": "bob@example.com",
                "password": "password123"
            }
            )
            token = login_response.json()["access_token"]
        
            response =  client.get(
            "/api/events/1/attendees",
        
            headers={"Authorization": f"Bearer {token}"}
            )
        
            assert response.status_code == 403


def test_get_attendee_list_with_invalid_token_returns_401():
    conn = get_connection()
    seed(conn)
    conn.close()
    app = create_app()

    with TestClient(app) as client:
            login_response =  client.post(
            "/auth/login",
            
            json={
                "email": "alice@example.com",
                "password": "password123"
            }
            )
            token = login_response.json()["access_token"]
        
            response =  client.get(
            "/api/events/1/attendees",
        
            headers={"Authorization": "Bearer invalidtoken"}
            )
            
          
 
            assert response.status_code == 401


def test_event_list_returns_401_with_invalid_token():
    conn=get_connection()
    seed(conn)
    conn.close()
    app = create_app()

    with TestClient(app) as client:

        
            response =  client.get(
            "/api/user/me/events",
        
            headers={"Authorization": "Bearer invalidtoken"}
            )

            assert response.status_code == 401




def test_get_events_list_for_authenticated_user_returns_200():
    conn = get_connection()
    seed(conn)
    conn.close()
    app = create_app()

    with TestClient(app) as client:
            login_response =  client.post(
            "/auth/login",
            
            json={
                "email": "bob@example.com",
                "password": "password123"
            }
            )
            token = login_response.json()["access_token"]
        
            response =  client.get(
            "/api/user/me/events",
        
            headers={"Authorization": f"Bearer {token}"}
            )
        
            assert response.status_code == 200
            data = response.json()

            assert "attendees" in data
            assert isinstance(data["attendees"], list)

            first_event = data["attendees"][0]

            assert isinstance(first_event["event_rank"], int)
            assert isinstance(first_event["total_rsvps"], int)




