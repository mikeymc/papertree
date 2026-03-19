import os
from unittest import mock
from unittest.mock import patch

import auth


def describe_init_oauth_client():
    def given_no_implicit_url():
        @patch("auth.OAUTH_REDIRECT_URI", "some-redirect-uri")
        @patch("auth.GOOGLE_CLIENT_ID", "some-client-id")
        @patch("auth.GOOGLE_CLIENT_SECRET", "some-client-secret")
        @patch("auth.Flow")
        def it_generates_and_returns_a_flow(Flow):
            Flow.from_client_config.return_value = "some-flow-object"

            return_value = auth.init_oauth_client()

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
                "redirect_uris": ["some-redirect-uri"],
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
            assert call_kwargs["redirect_uri"] == "some-redirect-uri"

            assert return_value == "some-flow-object"
