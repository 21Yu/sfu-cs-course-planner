from fastapi.testclient import TestClient
from app.models.courses import Course

def test_search_courses_returns_all(client: TestClient, session_factory):
    with session_factory() as db:
        course1 = Course(
            title = "Social Issues and Communication Strategies in Computing Science",
            course_code = "CMPT 105W",
            credits = 3,
            dept = "CMPT",
            number = "105W"
        )
        course2 = Course(
            title = "Probability and Computing",
            course_code = "CMPT 210",
            credits = 3,         
            dept = "CMPT",
            number = "210"
        )

        db.add_all([course1, course2])
        db.commit()

        response = client.get("/api/courses")
        data = response.json()

        assert response.status_code == 200
        assert data[0]["courseCode"] == "CMPT 105W"
        assert data[1]["courseCode"] == "CMPT 210"
        assert data[1]["title"] == "Probability and Computing"

def test_search_courses_by_query(client: TestClient, session_factory):
    with session_factory() as db:
        course1 = Course(
            title = "Social Issues and Communication Strategies in Computing Science",
            course_code = "CMPT 105W",
            credits = 3,
            dept = "CMPT",
            number = "105W"
        )
        db.add(course1)
        db.commit()

        response = client.get("/api/courses?q=comm")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["courseCode"] == "CMPT 105W"

def test_search_courses_by_subject(client: TestClient, session_factory):
    with session_factory() as db:
        course1 = Course(
            title = "Social Issues and Communication Strategies in Computing Science",
            course_code = "CMPT 105W",
            credits = 3,
            dept = "CMPT",
            number = "105W"
        )
        db.add(course1)
        db.commit()

        response = client.get("/api/courses?CMPT_105W")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["courseCode"] == "CMPT 105W"

def test_search_courses_limits_offsets(client: TestClient, session_factory):
    with session_factory() as db:
        course1 = Course(
            title = "Social Issues and Communication Strategies in Computing Science",
            course_code = "CMPT 105W",
            credits = 3,
            dept = "CMPT",
            number = "105W"
        )
        course2 = Course(
            title = "Probability and Computing",
            course_code = "CMPT 210",
            credits = 3,         
            dept = "CMPT",
            number = "210"
        )
        course3 = Course(
            title = "Numerical Analysis I",
            course_code = "MACM 316",
            credits = 3,         
            dept = "MACM",
            number = "316"
        )
        db.add_all([course1 ,course2, course3])
        db.commit()

        response = client.get("/api/courses?limit=1&offset=2")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["courseCode"] == "MACM 316"

def test_no_result_search(client: TestClient):
    response = client.get("/api/courses")
    data = response.json()

    assert response.status_code == 200
    assert data == []

def test_invalid_limit_offsets(client: TestClient):
    response = client.get("/api/courses?limit=0")
    assert response.status_code == 422

    response = client.get("/api/courses?limit=501")
    assert response.status_code == 422

    response = client.get("/api/courses?offset=-1")
    assert response.status_code == 422