import pytest
import jwt

from src.services.auth import AuthService
from src.exceptions import IncorrectTokenException


class TestAuthServiceUnit:
    def setup_method(self):
        self.auth_service = AuthService()

    def test_hash_password(self):
        hashed = self.auth_service.hash_password("my_secret_password")
        assert hashed
        assert isinstance(hashed, str)
        assert hashed != "my_secret_password"

    def test_verify_password_correct(self):
        hashed = self.auth_service.hash_password("my_secret_password")
        assert self.auth_service.verify_password("my_secret_password", hashed)

    def test_verify_password_incorrect(self):
        hashed = self.auth_service.hash_password("my_secret_password")
        assert not self.auth_service.verify_password("wrong_password", hashed)

    def test_create_access_token_contains_user_id(self):
        data = {"user_id": 42}
        token = self.auth_service.create_access_token(data)
        decoded = jwt.decode(
            token,
            self.auth_service.pwd_context,
            options={"verify_signature": False},
        )
        assert decoded["user_id"] == 42

    def test_create_access_token_has_expiry(self):
        data = {"user_id": 1}
        token = self.auth_service.create_access_token(data)
        decoded = jwt.decode(
            token,
            self.auth_service.pwd_context,
            options={"verify_signature": False},
        )
        assert "exp" in decoded

    def test_decode_token_valid(self):
        data = {"user_id": 7}
        token = self.auth_service.create_access_token(data)
        decoded = self.auth_service.decode_token(token)
        assert decoded["user_id"] == 7

    def test_decode_token_invalid_raises(self):
        with pytest.raises(IncorrectTokenException):
            self.auth_service.decode_token("invalid.jwt.token")
