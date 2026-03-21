import importlib
import os
from unittest.mock import Mock, patch

import auth
import pytest
from app import app, deps
from flask import session


@pytest.fixture
def db():
    return deps.db


def describe_init_oauth_client():
    @pytest.fixture(autouse=True)
    def reload_auth():
        yield
        importlib.reload(auth)

    def given_no_implicit_url():
        def it_generates_and_returns_a_flow():
            with patch.dict(
                os.environ,
                {
                    "OAUTH_REDIRECT_URI": "some-other-redirect-uri",
                    "GOOGLE_CLIENT_ID": "some-client-id",
                    "GOOGLE_CLIENT_SECRET": "some-client-secret",
                },
            ):
                importlib.reload(auth)
                with patch("auth.Flow") as Flow:
                    Flow.from_client_config.return_value = "some-flow-object"

                    return_value = auth.init_oauth_client()

                    Flow.from_client_config.assert_called_once()

                    call_args = Flow.from_client_config.call_args

                    assert len(call_args.args) == 1
                    first_arg = call_args.args[0]
                    assert "web" in first_arg
                    assert first_arg["web"] == {
                        "client_id": "some-client-id",
                        "client_secret": "some-client-secret",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["some-other-redirect-uri"],
                    }

                    call_kwargs = Flow.from_client_config.call_args.kwargs

                    assert len(call_kwargs) == 2
                    assert "scopes" in call_kwargs
                    assert call_kwargs["scopes"] == [
                        "openid",
                        "https://www.googleapis.com/auth/userinfo.email",
                        "https://www.googleapis.com/auth/userinfo.profile",
                    ]

                    assert "redirect_uri" in call_kwargs
                    assert call_kwargs["redirect_uri"] == "some-other-redirect-uri"

                    assert return_value == "some-flow-object"

    def given_an_explicit_redirect_url():
        @patch("auth.OAUTH_REDIRECT_URI", "oauth-redirect-uri")
        @patch("auth.Flow")
        def it_uses_the_explicit_redirect_uri(Flow):
            with patch.dict(
                os.environ,
                {
                    "GOOGLE_CLIENT_ID": "some-client-id",
                    "GOOGLE_CLIENT_SECRET": "some-client-secret",
                },
            ):
                Flow.from_client_config.return_value = "some-flow-object"

                return_value = auth.init_oauth_client("explicit-redirect-uri")

                Flow.from_client.config.assert_called_once

                call_args = Flow.from_client_config.call_args

                assert len(call_args.args) == 1
                first_arg = call_args.args[0]
                assert "web" in first_arg
                assert first_arg["web"] == {
                    "client_id": "some-client-id",
                    "client_secret": "some-client-secret",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["explicit-redirect-uri"],
                }

                call_kwargs = Flow.from_client_config.call_args.kwargs

                assert len(call_kwargs) == 2
                assert "scopes" in call_kwargs
                assert call_kwargs["scopes"] == [
                    "openid",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                ]

                assert "redirect_uri" in call_kwargs
                assert call_kwargs["redirect_uri"] == "explicit-redirect-uri"

                assert return_value == "some-flow-object"


def describe_require_user_auth():
    def given_no_user_id_in_session():
        def given_user_type_in_session():
            def it_adds_user_id_dev_bypass_to_wrapped_function_and_calls_it():
                with app.test_request_context("/"):
                    session["user_id"] = 123
                    session["user_type"] = "some-user-type"

                    @auth.require_user_auth
                    def dummy_function(arg1, arg2, user_id=id):
                        return arg1, arg2, user_id

                    arg1, arg2, user_id = dummy_function("first-arg", "second-arg")

                    assert arg1 == "first-arg"
                    assert arg2 == "second-arg"
                    assert user_id == 123

        def given_no_user_type_in_session():
            def it_defaults_to_regular_user(db):
                with app.test_request_context("/"):
                    session["user_id"] = 123

                    db.get_user_by_id = Mock(return_value={"foo": "bar"})

                    @auth.require_user_auth
                    def dummy_function(arg1, arg2, user_id=id):
                        return arg1, arg2, user_id

                    dummy_function("first-arg", "second-arg")

                    assert session["user_type"] == "regular"
                    db.get_user_by_id.assert_called_with(123)

            def it_adds_user_type_to_session(db):
                with app.test_request_context("/"):
                    session["user_id"] = 123

                    db.get_user_by_id = Mock(
                        return_value={"user_type": "some-user-type"}
                    )

                    @auth.require_user_auth
                    def dummy_function(arg1, arg2, user_id=id):
                        return arg1, arg2, user_id

                    dummy_function("first-arg", "second-arg")

                    assert session["user_type"] == "some-user-type"
                    db.get_user_by_id.assert_called_with(123)

        def given_user_id_not_in_session():
            def given_dev_auth_bypass_not_set():
                def it_returns_an_error_code_and_message():
                    with app.test_request_context("/"):

                        @auth.require_user_auth
                        def dummy_function(arg1, arg2, user_id=id):
                            return arg1, arg2, user_id

                        response, status_code = dummy_function(
                            "first-arg", "second-arg"
                        )

                        assert response.json == {
                            "error": "Unauthorized",
                            "message": "Please log in",
                        }

                        assert status_code == 401

            def given_dev_auth_bypass_is_set():
                @patch("auth.DEV_AUTH_BYPASS")
                def it_sets_dev_user_bypass_as_user_id(mock_auth_bypass):
                    with app.test_request_context("/"):
                        mock_auth_bypass = True

                        @auth.require_user_auth
                        def dummy_function(arg1, arg2, user_id=id):
                            return arg1, arg2, user_id

                        _, _, user_id = dummy_function("first-arg", "second-arg")

                        assert user_id == "dev-user-bypass"


def describe_https_settings():
    @pytest.fixture(autouse=True)
    def reload_auth():
        yield
        importlib.reload(auth)

    def describe_wxhen_localhost_is_redirect_uri():
        def it_sets_oauthlib_insecure_transport():
            with patch.dict(
                os.environ,
                {"OAUTH_REDIRECT_URI": "localhost"},
            ):
                importlib.reload(auth)
                assert "OAUTHLIB_INSECURE_TRANSPORT" in os.environ
                assert os.environ["OAUTHLIB_INSECURE_TRANSPORT"] == "1"

    def describe_when_redirect_uri_is_not_localhost():
        def it_does_not_set_oauthlib_insecure_transport():
            with patch.dict(
                os.environ,
                {
                    "OAUTH_REDIRECT_URI": "some-random-uri",
                    "OAUTHLIB_INSECURE_TRANSPORT": "toots",
                },
            ):
                importlib.reload(auth)
                assert os.environ["OAUTHLIB_INSECURE_TRANSPORT"] == "toots"

    def describe_when_localhost_ip_is_redirect_uri():
        def it_sets_oauthlib_insecure_transport():
            with patch.dict(
                os.environ,
                {
                    "OAUTH_REDIRECT_URI": "127.0.0.1",
                    "OAUTHLIB_INSECURE_TRANSPORT": "toots",
                },
            ):
                importlib.reload(auth)
                assert os.environ["OAUTHLIB_INSECURE_TRANSPORT"] == "1"


def describe_is_dev_auth_bypassed():
    @pytest.fixture(autouse=True)
    def reload_auth():
        yield
        importlib.reload(auth)

    def given_all_conditions_true():
        def given_localhost_is_part_of_uri():
            def it_returns_true():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "http://localhost:5000",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == True

            def it_sets_the_module_level_auth_bypass():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "http://localhost:5000",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == True

        def given_localhost_ip_is_part_of_uri():
            def it_returns_true():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "http://127.0.0.1:5000",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == True

        def given_redirect_to_localhost():
            def it_returns_true():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "localhost",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == True

                    # assert auth.is_dev_auth_bypassed() == True

        def given_redirect_to_localhost_ip():
            def it_returns_true():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "127.0.0.1",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == True

        def given_flask_env_is_production():
            def it_returns_false():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "127.0.0.1",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "production",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == False

        def given_dev_auth_bypass_is_false():
            def it_returns_false():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "127.0.0.1",
                        "DEV_AUTH_BYPASS": "false",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == False

        def given_oauth_redirect_uri_is_not_localhost():
            def it_returns_false():
                with patch.dict(
                    os.environ,
                    {
                        "OAUTH_REDIRECT_URI": "127.0.0.2",
                        "DEV_AUTH_BYPASS": "true",
                        "FLASK_ENV": "development",
                    },
                ):
                    importlib.reload(auth)
                    from auth import DEV_AUTH_BYPASS

                    assert DEV_AUTH_BYPASS == False
