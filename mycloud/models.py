from django.conf import settings
from django.db import models

from mycloud.utils import user_directory_path, seconds_since_epoch, generating_uuid


class File(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ID пользователя'
    )
    name = models.CharField(blank=True, null=True, max_length=255, verbose_name='Название файла')
    file = models.FileField(upload_to=user_directory_path, verbose_name='Сам файл')
    size = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='Размер файла, байт')
    data_created = models.PositiveBigIntegerField(default=seconds_since_epoch, verbose_name='Дата создания')
    date_download = models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Дата крайнего скачивания')
    comment = models.CharField(blank=True, null=True, max_length=500, verbose_name='Комментарий')
    hash = models.CharField(unique=True, default=generating_uuid, max_length=255, verbose_name='Название файла в хэш виде')

    def __str__(self):
        return self.name
