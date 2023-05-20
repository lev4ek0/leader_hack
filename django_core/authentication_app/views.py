from authentication_app.auth_vk import VKManager
from authentication_app.filters import UserFilter

from authentication_app.serializers import (
    TokenBlacklistSerializer,
    TokenRefreshSerializerWithBlacklist,
    UserListSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
)
from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseRedirect
from djoser.views import UserViewSet
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenViewBase

cache = caches["blacklist"]


class RedirectVK(APIView):
    """Вьюшка для редиректа на CAS авторизацию.
    В случае успешной авторазции возвращает нам на redirect_url код авторизации.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> HttpResponseRedirect:
        vk_manager = VKManager()

        next_param = request.GET.get("next", "")

        js_code = (
            f"window.localStorage.setItem('nextParam', '{next_param}');"
            f"window.location = '{vk_manager.obtain_auth_url()}'"
        )

        return HttpResponse(f"<script>{js_code}</script>")


class GetVKToken(APIView):
    """Вьюшка для получения токенов пользователя по коду авторазции"""

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        code = request.GET.get("code")

        vk_manager = VKManager()
        refresh_token, access_token = vk_manager.authorize(code)

        front_redirect_url = settings.BASE_URL

        js_code = (
            f"const nextParam = window.localStorage.getItem('nextParam');"
            f"const redirUrl = '/{front_redirect_url}';"
            f"const finalRedirectUrl = nextParam ? nextParam : redirUrl;"
            f"window.localStorage.setItem('access', '{str(access_token)}');"
            f"window.localStorage.setItem('refresh', '{str(refresh_token)}');"
            f"window.location = finalRedirectUrl;"
        )

        return HttpResponse(f"<script>{js_code}</script>")


class BlacklistTokenView(TokenViewBase):
    """
    Выход из системы, добавление refresh JWT в чёрный список.
    """

    serializer_class = TokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data["refresh"]
        token_in_cache = cache.get(token)

        if token_in_cache:
            return Response(
                {"error": "token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            cache.set(
                token,
                True,
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
            )

            return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshViewWithBlacklist(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer_class = TokenRefreshSerializerWithBlacklist


class CustomUserViewSet(UserViewSet):
    filterset_class = UserFilter

    def get_serializer_class(self):
        if self.action == "me" and self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        if self.action == "retrieve":
            return UserRetrieveSerializer
        if self.action == "all":
            return UserListSerializer
        return super().get_serializer_class()

    @extend_schema(responses=UserListSerializer(many=True))
    @action(
        detail=False,
        pagination_class=None,
    )
    def all(self, request):
        """
        Список пользователей без пагинации
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
