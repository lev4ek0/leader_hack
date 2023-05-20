from time import sleep

from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import Client, TestCase


User = get_user_model()

cache = caches["blacklist"]


class TokenBlacklistViewTests(TestCase):
    def setUp(self):

        self.client: Client = Client(CONTENT_TYPE="application/json")
        self.user: User = User.objects.create_user(
            email="test@test.com", password="testpassword"
        )

    def test_cannot_blacklist_random_token(self):
        """Не можем добавить в blacklist invlaid token"""
        response = self.client.post(
            "/api/v1/auth/jwt/blacklist/", {"refresh": "asdasd"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"detail": "Token is invalid or expired", "code": "token_not_valid"},
        )

    def test_can_blacklist_token(self):
        """Можем добавить в blacklist токен"""
        response = self.client.post(
            "/api/v1/auth/jwt/create/",
            {"email": self.user.email, "password": "testpassword"},
        )
        refresh = response.json()["refresh"]
        response = self.client.post("/api/v1/auth/jwt/blacklist/", {"refresh": refresh})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"refresh": refresh})

    def test_cannot_blacklist_blacklisted_token(self):
        """Не можем добавить токен, который уже в blacklist'е"""
        response = self.client.post(
            "/api/v1/auth/jwt/create/",
            {"email": self.user.email, "password": "testpassword"},
        )
        refresh = response.json()["refresh"]
        self.client.post("/api/v1/auth/jwt/blacklist/", {"refresh": refresh})
        response = self.client.post("/api/v1/auth/jwt/blacklist/", {"refresh": refresh})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "token already blacklisted"})

    def test_cannot_use_blacklisted_token(self):
        """Не можем использовать refresh token после добавления в blacklist"""
        response = self.client.post(
            "/api/v1/auth/jwt/create/",
            {"email": self.user.email, "password": "testpassword"},
        )
        refresh = response.json()["refresh"]

        response = self.client.post("/api/v1/auth/jwt/refresh/", {"refresh": refresh})
        self.assertEqual(response.status_code, 200)

        self.client.post("/api/v1/auth/jwt/blacklist/", {"refresh": refresh})

        response = self.client.post("/api/v1/auth/jwt/refresh/", {"refresh": refresh})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content, {"non_field_errors": ["Token is blacklisted"]}
        )

    def test_token_expires(self):
        response = self.client.post(
            "/api/v1/auth/jwt/create/",
            {"email": self.user.email, "password": "testpassword"},
        )
        refresh = response.json()["refresh"]
        response = self.client.post("/api/v1/auth/jwt/blacklist/", {"refresh": refresh})

        sleep(3)
        token_in_cache = cache.get(refresh)
        self.assertIsNone(token_in_cache)

        response = self.client.post("/api/v1/auth/jwt/refresh/", {"refresh": refresh})
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"detail": "Token is invalid or expired", "code": "token_not_valid"},
        )
