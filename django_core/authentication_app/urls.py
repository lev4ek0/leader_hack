from django.urls import include, path
from rest_framework.routers import DefaultRouter

from authentication_app.views import (BlacklistTokenView, CustomUserViewSet,
                                      GetVKToken, RedirectVK,
                                      TokenRefreshViewWithBlacklist)

app_name = "authentication_app"

router = DefaultRouter()
router.register("users", CustomUserViewSet)

urlpatterns = router.urls + [
    path("jwt/blacklist/", BlacklistTokenView.as_view()),
    path("jwt/refresh/", TokenRefreshViewWithBlacklist.as_view()),
    path("", include("djoser.urls.jwt")),
    path("vk_redirect/", RedirectVK.as_view()),
    path("oauth2/vk/", GetVKToken.as_view()),
]
