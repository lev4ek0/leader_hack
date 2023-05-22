import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from authentication_app.tasks import handle_user_avatar


User = get_user_model()


class VKManager:
    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(VKManager, cls).__new__(cls)
            for param_name, param_value in settings.VK_MANAGER_CONFIG.items():
                setattr(cls, param_name, param_value)

            cls.auth_url = f"{cls.base_uri}oauth/authorize?"
            cls.obtain_token_url = f"{cls.base_uri}access_token?"

        return cls._instance

    def obtain_auth_url(self):
        auth_url = "".join(
            [
                self.auth_url,
                f"response_type={self.response_type}&",
                f"scope={self.scope}&",
                f"client_id={self.client_id}&",
                f"redirect_uri={self.redirect_uri}",
            ]
        )

        return auth_url

    def authorize(self, code):

        payload = "&".join(
            [
                f"client_id={self.client_id}",
                f"client_secret={self.client_secret}",
                f"redirect_uri={self.redirect_uri}",
                f"code={code}",
            ]
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.request(
            "GET", self.obtain_token_url + payload, headers=headers
        )
        print(self.obtain_token_url + payload)
        print(response.text)
        resp_json = response.json()
        return self.get_or_create_user(resp_json.get("access_token"), resp_json.get("email"))

    def create_user(self, user_data):
        first_name, last_name, access_token, email, vk_id = (
            user_data.get("first_name"),
            user_data.get("last_name"),
            user_data.get("access_token"),
            user_data.get("email"),
            user_data.get("user_id"),
        )

        user = User.objects.create(
            vk=vk_id,
            email=email,
            vk_access_token=access_token,
            first_name=first_name,
            last_name=last_name,
            is_email_verified=True,
        )

        # handle_user_avatar.delay(pk=user.pk, picture=user_data.get("picture"))

        return user

    def get_or_create_user(self, access_token, email):

        user_data = requests.post(
            "https://api.vk.com/method/users.get",
            data={
                'access_token': access_token,
                'v': '5.131',
            }
        ).json().get('response', [{}])[0]
        user_data['access_token'] = access_token
        user_data['email'] = email
        user = User.objects.filter(
            email=email
        ).first()
        if not user:
            user = self.create_user(user_data=user_data)
            user.set_unusable_password()

        refresh = RefreshToken.for_user(user)

        return str(refresh), str(refresh.access_token)
