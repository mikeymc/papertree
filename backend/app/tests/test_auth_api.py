import os
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
    def when_no_credentials():
        def it_returns_400(client):
            response = client.post("/api/auth/login", json={})
            assert response.status_code == 400
            assert response.json == {"error": "No data provided"}

    def when_with_email_and_no_password():
        def it_returns_400(client):
            response = client.post("/api/auth/login", json={"email": "mc@hammer.com"})
            assert response.status_code == 400
            assert response.json == {"error": "Email and password are required"}

    def when_password_and_no_email():
        def it_returns_400(client):
            response = client.post("/api/auth/login", json={"password": "bananas"})
            assert response.status_code == 400
            assert response.json == {"error": "Email and password are required"}

    def when_user_not_found():
        def it_returns_401(client):
            db.get_user_by_email = Mock(return_value=None)

            response = client.post(
                "/api/auth/login",
                json={"email": "mc@hammer.com", "password": "bananas"},
            )
            assert response.status_code == 401
            assert response.json == {"error": "Invalid email or password"}

    def describe_user_password_checking():
        def when_user_has_no_password_hash():
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

        def when_user_password_hash_does_not_match():
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

    def given_user_not_verified():
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

    def given_successful():
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

    def given_an_error():
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


def describe_logout():
    def it_returns_200_and_a_message(client):
        response = client.post("/api/auth/logout")

        assert response.status_code == 200
        assert response.json == {"message": "Logged out successfully"}

    def it_clears_the_session(client):
        with client.session_transaction() as sess:
            sess["user_id"] = {"id": 1234}

        client.post("/api/auth/logout")

        with client.session_transaction() as sess:
            assert "user_id" not in sess


def describe_verify_user():
    def it_checks_the_otp_code_and_user_email(client, db):
        db.verify_user_otp = Mock(return_value=True)

        client.post(
            "/api/auth/verify", json={"code": "otp-code", "email": "mc@hammer.com"}
        )

        db.verify_user_otp.assert_called_once_with("mc@hammer.com", "otp-code")

    def when_the_verification_succeeds():
        def it_responds_with_success(client, db):
            db.verify_user_otp = Mock(return_value=True)

            response = client.post(
                "/api/auth/verify", json={"code": "otp-code", "email": "mc@hammer.com"}
            )

            assert response.status_code == 200
            assert response.json == {"message": "Email verified successfully"}

    def when_the_verification_fails():
        def it_responds_with_failure(client, db):
            db.verify_user_otp = Mock(return_value=False)

            response = client.post(
                "/api/auth/verify", json={"code": "otp-code", "email": "mc@hammer.com"}
            )

            assert response.status_code == 400
            assert response.json == {"error": "Invalid, expired, or incorrect code"}

    def when_there_is_an_exception():
        def it_responds_with_failure(client, db):
            db.verify_user_otp = Mock(side_effect=KeyError("foo"))

            response = client.post(
                "/api/auth/verify", json={"code": "otp-code", "email": "mc@hammer.com"}
            )

            assert response.status_code == 500
            assert response.json["error"] is not None


def describe_complete_onboarding():
    def given_user_not_logged_in():
        def it_responds_with_failure(client, db):
            with client.session_transaction() as session:
                session.pop("user_id", None)

            db.mark_onboarding_complete = Mock()

            response = client.post("/api/user/complete_onboarding")

            assert response.status_code == 401
            assert response.json == {"error": "Not authenticated"}
            db.mark_onboarding_complete.assert_not_called()

    def given_user_logged_in():
        def it_marks_onboarding_complete_in_the_db(client, db):
            with client.session_transaction() as session:
                session["user_id"] = "1234"

            db.mark_onboarding_complete = Mock()

            response = client.post("/api/user/complete_onboarding")

            assert response.status_code == 200
            assert response.json == {"message": "Onboarding completed"}
            db.mark_onboarding_complete.assert_called_once_with("1234")

    def given_there_is_an_error():
        def it_returns_a_500_error(client, db):
            with client.session_transaction() as session:
                session["user_id"] = "1234"

            db.mark_onboarding_complete = Mock(side_effect=Exception("Database error"))

            response = client.post("/api/user/complete_onboarding")

            assert response.status_code == 500
            assert response.json == {"error": "Database error"}


def describe_register():
    def describe_sad_paths():
        def when_no_data_is_posted():
            def it_returns_a_400(client):
                response = client.post("/api/auth/register", json={})

                assert response.status_code == 400
                assert response.json == {"error": "No data provided"}

        def when_email_is_not_posted():
            def it_returns_a_400(client):
                response = client.post(
                    "/api/auth/register",
                    json={
                        "password": "foo",
                        "name": "bar",
                    },
                )

                assert response.status_code == 400
                assert response.json == {"error": "Email and password are required"}

        def when_password_is_not_posted():
            def it_returns_a_400(client):
                response = client.post(
                    "/api/auth/register",
                    json={
                        "email": "foo",
                        "name": "bar",
                    },
                )

                assert response.status_code == 400
                assert response.json == {"error": "Email and password are required"}

        def given_user_already_registered():
            def it_returns_a_400(client, db):
                db.get_user_by_email = Mock(return_value=True)

                response = client.post(
                    "/api/auth/register",
                    json={
                        "email": "foo",
                        "password": "bar",
                    },
                )

                assert response.status_code == 400
                assert response.json == {"error": "Email already registered"}

        def given_there_is_an_error():
            @patch("app.auth.logger")
            def it_returns_500_and_logs_the_error(mock_logger, client):
                response = client.post("/api/auth/register", json=None)

                assert response.status_code == 500
                assert response.json == {
                    "error": "415 Unsupported Media Type: Did not attempt to load JSON data because the request Content-Type was not 'application/json'."
                }
                mock_logger.error.assert_called_with(
                    "Registration error: 415 Unsupported Media Type: Did not attempt to load JSON data because the request Content-Type was not 'application/json'."
                )

    def describe_successful_new_user_flow():
        @patch("app.auth.send_verification_email")
        @patch("app.auth.generate_password_hash")
        @patch("app.auth.logger")
        @patch("app.auth.generate_verification_code")
        @patch("app.auth.generate_expiration_date")
        def it_hashes_password_creates_user_and_sends_email(
            mock_generate_expiration_date,
            mock_generate_verification_code,
            mock_logger,
            mock_password_hash,
            mock_send_verification_email,
            client,
            db,
        ):
            mock_password_hash.return_value = "mock-hash-value"
            db.get_user_by_email = Mock(return_value=False)
            db.create_user_with_password = Mock(return_value="some-user-id")
            mock_generate_verification_code.return_value = "some-otp-code"
            mock_generate_expiration_date.return_value = "some-expiration-date"
            mock_send_verification_email.return_value = True

            response = client.post(
                "/api/auth/register",
                json={
                    "email": "foo@hammertime.com",
                    "password": "bar",
                    "name": "mc-hammer",
                },
            )

            db.get_user_by_email.assert_called_with("foo@hammertime.com")
            mock_password_hash.assert_called_with("bar")
            db.create_user_with_password.assert_called_with(
                "foo@hammertime.com",
                "mock-hash-value",
                "mc-hammer",
                "some-otp-code",
                "some-expiration-date",
            )
            mock_send_verification_email.assert_called_with(
                "foo@hammertime.com", "some-otp-code"
            )
            mock_logger.info.assert_called_with(
                "Verification email sent to foo@hammertime.com"
            )
            assert response.status_code == 200
            assert response.json == {
                "message": "Registration successful. Please check your email for the verification code.",
                "user": {
                    "id": "some-user-id",
                    "email": "foo@hammertime.com",
                    "name": "mc-hammer",
                    "has_completed_onboarding": False,
                },
            }

        def describe_when_no_name_is_provided():
            @patch("app.auth.generate_password_hash")
            @patch("app.auth.generate_verification_code")
            @patch("app.auth.generate_expiration_date")
            @patch("app.auth.send_verification_email")
            def it_uses_the_email_address_name(
                verification_email_mock,
                mock_generate_expiration_date,
                mock_generate_verification_code,
                mock_password_hash,
                client,
                db,
            ):
                verification_email_mock.return_value = True
                mock_password_hash.return_value = "mock-hash-value"
                db.get_user_by_email = Mock(return_value=False)
                db.create_user_with_password = Mock(return_value="some-user-id")
                mock_generate_verification_code.return_value = "some-otp-code"
                mock_generate_expiration_date.return_value = "some-expiration-date"

                client.post(
                    "/api/auth/register",
                    json={
                        "email": "foo@hammertime.com",
                        "password": "bar",
                    },
                )

                db.create_user_with_password.assert_called_with(
                    "foo@hammertime.com",
                    "mock-hash-value",
                    "foo",
                    "some-otp-code",
                    "some-expiration-date",
                )

        def given_email_send_fails():
            @patch("app.auth.send_verification_email")
            @patch("app.auth.generate_password_hash")
            @patch("app.auth.logger")
            @patch("app.auth.generate_verification_code")
            @patch("app.auth.generate_expiration_date")
            def it_logs_the_failure(
                mock_generate_expiration_date,
                mock_generate_verification_code,
                mock_logger,
                mock_password_hash,
                mock_send_verification_email,
                client,
                db,
            ):
                mock_password_hash.return_value = "mock-hash-value"
                db.get_user_by_email = Mock(return_value=False)
                db.create_user_with_password = Mock(return_value="some-user-id")
                mock_generate_verification_code.return_value = "some-otp-code"
                mock_generate_expiration_date.return_value = "some-expiration-date"
                mock_send_verification_email.return_value = False

                client.post(
                    "/api/auth/register",
                    json={
                        "email": "foo@hammertime.com",
                        "password": "bar",
                    },
                )

                mock_logger.error.assert_called_with(
                    "Failed to send verification email to foo@hammertime.com"
                )
                mock_logger.info.assert_called_with(
                    "EMAILS FAILED - VERIFICATION CODE FOR foo@hammertime.com: some-otp-code"
                )


def describe_test_login():
    def given_test_auth_not_enabled():
        def it_returns_a_403(client):
            with patch.dict(os.environ, {"ENABLE_TEST_AUTH": "false"}):
                response = client.post("/api/auth/test-login", json={})

                assert response.status_code == 403
                assert response.json == {"error": "Test auth not enabled"}

    def describe_when_test_auth_enabled():
        def it_creates_a_test_user(client, db):
            with patch.dict(os.environ, {"ENABLE_TEST_AUTH": "true"}):
                db.create_user = Mock(return_value="user-id")

                response = client.post("/api/auth/test-login", json={})

                assert response.status_code == 200
                assert response.json["message"] == "Test login successful"
                assert response.json == {
                    "message": "Test login successful",
                    "user": {
                        "id": "user-id",
                        "email": "test@example.com",
                        "name": "Test User",
                        "picture": "https://example.com/test.jpg",
                    },
                }

        def it_adds_user_to_session(client, db):
            with client.session_transaction() as sess:
                assert "user_id" not in sess
                assert "user_email" not in sess
                assert "user_name" not in sess
                assert "user_picture" not in sess

            db.create_user = Mock(return_value="user-id")
            with patch.dict(os.environ, {"ENABLE_TEST_AUTH": "true"}):
                client.post("/api/auth/test-login", json={})

            with client.session_transaction() as sess:
                assert sess["user_id"] == "user-id"
                assert sess["user_email"] == "test@example.com"
                assert sess["user_name"] == "Test User"
                assert sess["user_picture"] == "https://example.com/test.jpg"

    def given_an_exception():
        @patch("app.auth.logger")
        def it_returns_500_and_logs_error(mock_logger, client, db):
            with patch.dict(os.environ, {"ENABLE_TEST_AUTH": "true"}):
                db.create_user = Mock(side_effect=Exception("error message"))

                response = client.post("/api/auth/test-login", json={})

                assert response.status_code == 500
                assert response.json == {"error": "error message"}
                mock_logger.error.assert_called_with("Test login error: error message")


def describe_get_current_user():
    def given_no_user_in_session():
        def it_returns_a_401(client):
            response = client.get("/api/auth/user")

            assert response.status_code == 401
            assert response.json == {"error": "Not authenticated"}

    def given_user_not_registered():
        def it_returns_a_401(client, db):
            with client.session_transaction() as sess:
                sess["user_id"] = {"id": 1234}

            db.get_user_by_id = Mock(return_value=None)

            response = client.get("/api/auth/user")

            assert response.status_code == 401
            assert response.json == {"error": "User not found"}

            with client.session_transaction() as sess:
                assert "user_id" not in sess

    def given_user_registered_and_in_session():
        def it_returns_the_user(client, db):
            with client.session_transaction() as sess:
                sess["user_id"] = {"id": 1234}

            fake_user = {
                "id": "1234",
                "email": "mc@hammer.com",
                "name": "mr-hammer",
                "picture": "some-picture",
                "feature_flags": "some-feature-flags",
                "has_completed_onboarding": True,
                "user_type": "some-user-type",
            }
            db.get_user_by_id = Mock(return_value=fake_user)

            response = client.get("/api/auth/user")

            assert response.status_code == 200
            assert response.json == fake_user


def describe_get_google_auth_url():
    @patch("app.auth.init_oauth_client")
    def it_passes_the_redirect_url_to_the_initializer(mock_init_auth, client):
        mock_flow = Mock()
        mock_flow.authorization_url = Mock(return_value=("auth-url", "some-state"))
        mock_init_auth.return_value = mock_flow

        client.get("/api/auth/google/url", base_url="https://base-url")

        mock_init_auth.assert_called_with(
            redirect_uri="https://base-url/api/auth/google/callback"
        )

    @patch("app.auth.generate_pkce_challenge_and_verifier")
    @patch("app.auth.init_oauth_client")
    def it_calls_flow_to_get_the_state_and_auth_url(
        mock_init_auth, mock_challenger, client
    ):
        mock_flow = Mock()
        mock_flow.authorization_url = Mock(return_value=("auth-url", "some-state"))
        mock_init_auth.return_value = mock_flow
        mock_challenger.return_value = "some-verifier", "some-code-challenge"

        client.get("/api/auth/google/url", base_url="https://base-url")

        call_kwargs = mock_flow.authorization_url.call_args[1]
        assert call_kwargs["access_type"] == "offline"
        assert call_kwargs["include_granted_scopes"] == "true"
        assert call_kwargs["code_challenge_method"] == "S256"
        assert call_kwargs["code_challenge"] == "some-code-challenge"

    @patch("app.auth.generate_pkce_challenge_and_verifier")
    @patch("app.auth.init_oauth_client")
    def it_puts_the_code_verifier_in_the_state(mock_init_auth, mock_challenger, client):
        mock_flow = Mock()
        mock_flow.authorization_url = Mock(return_value=("auth-url", "some-state"))
        mock_init_auth.return_value = mock_flow
        mock_challenger.return_value = "some-verifier", "some-code-challenge"

        response = client.get("/api/auth/google/url")

        assert response.status_code == 200
        assert response.json == {"url": "auth-url"}

        with client.session_transaction() as sess:
            assert "oauth_code_verifier" in sess

    @patch("app.auth.init_oauth_client")
    def it_responds_with_200_and_google_oauth_url(mock_init_auth, client):
        mock_flow = Mock()
        mock_flow.authorization_url = Mock(return_value=("auth-url", "some-state"))
        mock_init_auth.return_value = mock_flow

        response = client.get("/api/auth/google/url")

        assert response.status_code == 200
        assert response.json == {"url": "auth-url"}

    @patch("app.auth.init_oauth_client")
    def it_sets_session_state(mock_init_auth, client):
        with client.session_transaction() as sess:
            assert "oauth-state" not in sess

        mock_flow = Mock()
        mock_flow.authorization_url = Mock(return_value=("auth-url", "some-state"))
        mock_init_auth.return_value = mock_flow

        response = client.get("/api/auth/google/url")

        assert response.status_code == 200
        assert response.json == {"url": "auth-url"}
        with client.session_transaction() as sess:
            assert "oauth_state" in sess
            assert sess["oauth_state"] == "some-state"
            assert "oauth_code_verifier" in sess

    def given_an_error():
        @patch("app.auth.init_oauth_client")
        def it_returns_500_and_a_message(mock_init_auth, client):
            mock_init_auth.side_effect = Exception("some-exception")

            response = client.get("/api/auth/google/url")

            assert response.status_code == 500
            assert response.json == {"error": "some-exception"}


def describe_google_auth_callback():
    def given_no_auth_code_in_the_request_args():
        def it_returns_400(client):
            response = client.get("/api/auth/google/callback")

            assert response.status_code == 400
            assert response.json == {"error": "No authorization code provided"}

    def given_auth_code_but_oauth_state_mismatch():
        def it_returns_400(client):
            with client.session_transaction() as sess:
                sess["oauth_state"] = "session-oauth-state"

            response = client.get(
                "/api/auth/google/callback",
                query_string={"code": "some-code", "state": "some-other-state"},
            )

            assert response.status_code == 400
            assert response.json == {"error": "Invalid state parameter"}

    def given_is_an_exception():
        @patch("app.auth.id_token")
        @patch("app.auth.init_oauth_client")
        @patch("app.auth.logger")
        def it_returns_a_500(mock_logger, mock_init_oauth, mock_id_token, client, db):
            with client.session_transaction() as sess:
                sess["oauth_state"] = "session-oauth-state"

            mock_flow = Mock()
            mock_flow.fetch_token = Mock()
            mock_flow.credentials.id_token = "some-id-token"
            mock_init_oauth.return_value = mock_flow

            mock_id_token.verify_oauth2_token.side_effect = Exception("some-exception")

            db.create_user = Mock(return_value="some-user-id")
            db.get_user_by_id = Mock(return_value={})

            response = client.get(
                "/api/auth/google/callback",
                query_string={
                    "code": "some-code",
                    "state": "session-oauth-state",
                },
            )

            assert response.status_code == 500
            assert response.json == {"error": "some-exception"}
            mock_logger.error.assert_called_with("OAuth callback error: some-exception")

    def describe_normal_flow():
        @patch("app.auth.id_token")
        @patch("app.auth.init_oauth_client")
        @patch("app.auth.redirect")
        def it_redirects_to_the_frontend_url(
            mock_redirect, mock_init_oauth, mock_id_token, client, db
        ):
            with client.session_transaction() as sess:
                sess["oauth_state"] = "session-oauth-state"

            with patch.dict(os.environ, {"FRONTEND_URL": "frontend-url"}):
                mock_flow = Mock()
                mock_flow.fetch_token = Mock()
                mock_flow.credentials.id_token = "some-id-token"
                mock_init_oauth.return_value = mock_flow

                mock_id_token.verify_oauth2_token.return_value = {
                    "sub": "some-google-id",
                    "email": "some-email",
                    "name": "some-name",
                    "picture": "some-picture",
                }

                db.create_user = Mock(return_value="some-user-id")
                db.get_user_by_id = Mock(return_value={"user_type": "some-user-type"})

                client.get(
                    "/api/auth/google/callback",
                    query_string={"code": "some-code", "state": "session-oauth-state"},
                )

                mock_redirect.assert_called_with("frontend-url")

        @patch("app.auth.id_token")
        @patch("app.auth.init_oauth_client")
        @patch("app.auth.redirect")
        def it_creates_a_user(
            mock_redirect, mock_init_oauth, mock_id_token, client, db
        ):
            with client.session_transaction() as sess:
                sess["oauth_state"] = "session-oauth-state"

            with patch.dict(os.environ, {"FRONTEND_URL": "frontend-url"}):
                mock_flow = Mock()
                mock_flow.fetch_token = Mock()
                mock_flow.credentials.id_token = "some-id-token"
                mock_init_oauth.return_value = mock_flow

                mock_id_token.verify_oauth2_token.return_value = {
                    "sub": "some-google-id",
                    "email": "some-email",
                    "name": "some-name",
                    "picture": "some-picture",
                }

                db.create_user = Mock(return_value="some-user-id")
                db.get_user_by_id = Mock(return_value={"user_type": "some-user-type"})

                client.get(
                    "/api/auth/google/callback",
                    query_string={"code": "some-code", "state": "session-oauth-state"},
                )

                db.create_user.assert_called_with(
                    "some-google-id", "some-email", "some-name", "some-picture"
                )

        @patch("app.auth.id_token")
        @patch("app.auth.init_oauth_client")
        def it_sets_the_user_in_the_session_and_removes_the_oauth_session_state(
            mock_init_oauth, mock_id_token, client, db
        ):
            with client.session_transaction() as sess:
                sess["oauth_state"] = "session-oauth-state"

            with patch.dict(os.environ, {"FRONTEND_URL": "frontend-url"}):
                mock_flow = Mock()
                mock_flow.fetch_token = Mock()
                mock_flow.credentials.id_token = "some-id-token"
                mock_init_oauth.return_value = mock_flow

                mock_id_token.verify_oauth2_token.return_value = {
                    "sub": "some-google-id",
                    "email": "some-email",
                    "name": "some-name",
                    "picture": "some-picture",
                }

                db.create_user = Mock(return_value="some-user-id")
                db.get_user_by_id = Mock(return_value={"user_type": "some-user-type"})

                client.get(
                    "/api/auth/google/callback",
                    query_string={"code": "some-code", "state": "session-oauth-state"},
                )

            with client.session_transaction() as sess:
                assert "oauth_state" not in sess
                assert sess["user_id"] == "some-user-id"
                assert sess["user_email"] == "some-email"
                assert sess["user_name"] == "some-name"
                assert sess["user_picture"] == "some-picture"
                assert sess["user_type"] == "some-user-type"

        def given_the_user_does_not_have_a_user_type():
            @patch("app.auth.id_token")
            @patch("app.auth.init_oauth_client")
            def it_sets_the_user_as_regular_type(
                mock_init_oauth, mock_id_token, client, db
            ):
                with client.session_transaction() as sess:
                    sess["oauth_state"] = "session-oauth-state"

                with patch.dict(os.environ, {"FRONTEND_URL": "frontend-url"}):
                    mock_flow = Mock()
                    mock_flow.fetch_token = Mock()
                    mock_flow.credentials.id_token = "some-id-token"
                    mock_init_oauth.return_value = mock_flow

                    mock_id_token.verify_oauth2_token.return_value = {
                        "sub": "some-google-id",
                        "email": "some-email",
                        "name": "some-name",
                        "picture": "some-picture",
                    }

                    db.create_user = Mock(return_value="some-user-id")
                    db.get_user_by_id = Mock(return_value={})

                    client.get(
                        "/api/auth/google/callback",
                        query_string={
                            "code": "some-code",
                            "state": "session-oauth-state",
                        },
                    )

                with client.session_transaction() as sess:
                    assert sess["user_type"] == "regular"

        def given_the_frontend_url_environment_variable_is_not_set():
            @patch("app.auth.id_token")
            @patch("app.auth.init_oauth_client")
            @patch("app.auth.redirect")
            def it_redirects_to_a_default_url(
                mock_redirect, mock_init_oauth, mock_id_token, client, db
            ):
                with client.session_transaction() as sess:
                    sess["oauth_state"] = "session-oauth-state"

                mock_flow = Mock()
                mock_flow.fetch_token = Mock()
                mock_flow.credentials.id_token = "some-id-token"
                mock_init_oauth.return_value = mock_flow

                mock_id_token.verify_oauth2_token.return_value = {
                    "sub": "some-google-id",
                    "email": "some-email",
                    "name": "some-name",
                    "picture": "some-picture",
                }

                db.create_user = Mock(return_value="some-user-id")
                db.get_user_by_id = Mock(return_value={})

                client.get(
                    "/api/auth/google/callback",
                    query_string={
                        "code": "some-code",
                        "state": "session-oauth-state",
                    },
                )

                mock_redirect.assert_called_with("http://localhost:5173")
