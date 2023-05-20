from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from django.contrib.auth import get_user_model

# from django_core.celery import app


User = get_user_model()


# @app.task
def handle_user_avatar(pk: int, picture: str) -> None:
    """Таска в celery для обработки аватара пользователя"""

    user = User.objects.get(pk=pk)
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(picture).read())
    img_temp.flush()
    user.picture.save(f"image_{user.pk}.jpg", File(img_temp))
