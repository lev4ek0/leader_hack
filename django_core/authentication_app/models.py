from authentication_app.managers import UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from utils.basemodel import BaseModel


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    vk = models.CharField(
        verbose_name=_("Идентификатор vk"), max_length=150, blank=True
    )
    vk_access_token = models.CharField(
        verbose_name=_("Токен вк"), max_length=150, blank=True
    )
    first_name = models.CharField(verbose_name=_("Имя"), max_length=150)
    middle_name = models.CharField(
        verbose_name=_("Отчество"), max_length=150, blank=True
    )
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=150)
    phone_number = models.CharField(
        max_length=15, verbose_name="Номер телефона", blank=True
    )
    is_staff = models.BooleanField(
        verbose_name=_("Менеджер"),
        default=False,
        help_text="Дает доступ к админке",
    )
    email = models.EmailField(verbose_name=_("Адрес электронной почты"), unique=True)
    picture = models.ImageField(
        verbose_name=_("Аватар пользователя"),
        upload_to="avatars/%Y/%m/%d/",
        blank=True,
        null=True,
    )

    is_email_verified = models.BooleanField(
        verbose_name=_("Статус подтверждения email"),
        default=False,
    )

    date_joined = models.DateTimeField(_("дата создания"), default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "middle_name",
    ]

    objects = UserManager()

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}"

    def __str__(self) -> str:
        return str(self.email)

    # class Meta:
    #     ordering = ("last_name", "first_name", "middle_name", "id")


# class ProxyUser(User):
#     class Meta:
#         proxy = True
#         app_label = "auth"
#         verbose_name = "Пользователь"
#         verbose_name_plural = "Пользователи"

