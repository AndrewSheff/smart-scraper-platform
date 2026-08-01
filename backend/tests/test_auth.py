"""Тесты аутентификации — логин, регистрация, токены, смена пароля."""

import pytest

from app.core.security import create_access_token, hash_password, verify_password, verify_token


class TestSecurity:
    """Тесты утилит безопасности."""

    def test_hash_password(self):
        """Хеш пароля должен быть разным от самого пароля."""
        password = "mysecretpass"
        hashed = hash_password(password)
        assert hashed != password
        assert hashed.startswith("$2")

    def test_verify_password_correct(self):
        """Верный пароль должен проходить проверку."""
        password = "mysecretpass"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Неверный пароль не должен проходить."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_create_access_token(self):
        """Токен должен создаваться и содержать данные."""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_token(self):
        """Декодирование токена должно вернуть payload."""
        data = {"sub": "user-123", "email": "test@example.com", "role": "user"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"

    def test_verify_invalid_token(self):
        """Невалидный токен должен бросать исключение."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            verify_token("invalid-token-lol")


class TestTokenPayload:
    """Тесты структуры JWT payload."""

    def test_token_contains_exp(self):
        """Токен должен содержать время истечения."""
        token = create_access_token({"sub": "123"})
        payload = verify_token(token)
        assert "exp" in payload

    def test_token_contains_custom_data(self):
        """Кастомные данные должны сохраняться в токене."""
        data = {
            "sub": "user-id",
            "email": "me@example.com",
            "name": "Test",
            "role": "admin",
            "must_change_password": False,
        }
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload["name"] == "Test"
        assert payload["role"] == "admin"
