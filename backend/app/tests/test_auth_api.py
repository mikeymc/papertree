from unittest.mock import Mock, patch

import pytest
from app import app, deps


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def db():
    return deps.db


def describe_login():
    def describe_when_no_credentials():
        def it_returns_400(client):
            response = client.post("/api/auth/login", json={})
            assert response.status_code == 400
            assert response.json == {"error": "No data provided"}

    def describe_with_email_and_no_password():
        def it_returns_400(client):
            response = client.post("/api/auth/login", json={"email": "mc@hammer.com"})
            assert response.status_code == 400
            assert response.json == {"error": "Email and password are required"}

    def describe_with_password_and_no_email():
        def it_returns_400(client):
            response = client.post("/api/auth/login", json={"password": "bananas"})
            assert response.status_code == 400
            assert response.json == {"error": "Email and password are required"}

    def describe_with_user_not_found():
        def it_returns_401(client):
            db.get_user_by_email = Mock(return_value=None)

            response = client.post(
                "/api/auth/login",
                json={"email": "mc@hammer.com", "password": "bananas"},
            )
            assert response.status_code == 401
            assert response.json == {"error": "Invalid email or password"}

    def describe_user_password_checking():
        def describe_user_without_password_hash():
            def it_returns_401(client, db):
                db.get_user_by_email = Mock(
                    return_value={"email": "mc@hammer.com", "password_hash": None}
                )

                response = client.post(
                    "/api/auth/login",
                    json={"email": "mc@hammer.com", "password": "bananas"},
                )
                assert response.status_code == 401
                assert response.json == {"error": "Please sign in with Google"}

        def describe_how_the_password_check_works():
            @patch("app.auth.check_password_hash")
            def it_calls_werkzeug_check_password_hash(mock_check_password, client, db):
                db.get_user_by_email = Mock(
                    return_value={
                        "email": "mc@hammer.com",
                        "password_hash": "stored-password-hash",
                        "password": "stored-password",
                    }
                )

                mock_check_password.return_value = False

                client.post(
                    "/api/auth/login",
                    json={"email": "mc@hammer.com", "password": "provided-password"},
                )

                mock_check_password.assert_called_with(
                    "stored-password-hash", "provided-password"
                )

        def describe_with_user_password_hash_mismatch():
            @patch("app.auth.check_password_hash")
            def it_returns_401(mock_check_password, client, db):
                db.get_user_by_email = Mock(
                    return_value={
                        "email": "mc@hammer.com",
                        "password_hash": "fake-hash",
                        "password": "fake-password",
                    }
                )

                mock_check_password.return_value = False

                response = client.post(
                    "/api/auth/login",
                    json={"email": "mc@hammer.com", "password": "bananas"},
                )
                assert response.status_code == 401
                assert response.json == {"error": "Invalid email or password"}

    def describe_with_user_not_verified():
        @patch("app.auth.check_password_hash")
        def it_returns_403(mock_check_password, client, db):
            db.get_user_by_email = Mock(
                return_value={
                    "email": "mc@hammer.com",
                    "password_hash": "fake-hash",
                    "is_verified": False,
                }
            )

            mock_check_password.return_value = True

            response = client.post(
                "/api/auth/login",
                json={"email": "mc@hammer.com", "password": "bananas"},
            )
            assert response.status_code == 403
            assert response.json == {
                "error": "Email not verified. Please check your inbox."
            }

    def describe_given_successful():
        @patch("app.auth.check_password_hash")
        def it_returns_200_and_user_information(mock_check_password, client, db):
            db.get_user_by_email = Mock(
                return_value={
                    "email": "mc@hammer.com",
                    "password_hash": "fake-hash",
                    "is_verified": True,
                    "id": 1234,
                    "name": "MC Hammer",
                    "picture": "some-picture",
                }
            )
            mock_check_password.return_value = True
            db.update_last_login = Mock()

            response = client.post(
                "/api/auth/login",
                json={"email": "mc@hammer.com", "password": "bananas"},
            )
            assert response.status_code == 200
            assert response.json["message"] == "Login successful"
            assert response.json["user"] == {
                "id": 1234,
                "email": "mc@hammer.com",
                "name": "MC Hammer",
                "picture": "some-picture",
                "has_completed_onboarding": False,
            }

    def describe_given_error():
        @patch("app.auth.check_password_hash")
        def it_returns_500_and_error_message(mock_check_password, client, db):
            db.get_user_by_email = Mock(
                return_value={
                    "email": "mc@hammer.com",
                    "password_hash": "fake-hash",
                    "is_verified": True,
                }
            )
            mock_check_password.return_value = True

            response = client.post(
                "/api/auth/login",
                json={"email": "mc@hammer.com", "password": "bananas"},
            )
            assert response.status_code == 500
            assert response.json == {"error": "'id'"}

        # @patch("app.auth.session")


def describe_logout():
    def it_returns_200_and_a_message(client):
        response = client.post("/api/auth/logout")

        # assert mock_session.clear.called
        assert response.status_code == 200
        assert response.json == {"message": "Logged out successfully"}

    def it_clears_the_session(client):
        with client.session_transaction() as sess:
            sess["user_id"] = {"id": 1234}

        client.post("/api/auth/logout")

        with client.session_transaction() as sess:
            assert "user_id" not in sess
