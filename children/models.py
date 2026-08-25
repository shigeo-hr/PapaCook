from django.conf import settings
from django.db import models


class Child(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children', verbose_name='保護者',
    )
    name = models.CharField('名前', max_length=50)
    age = models.PositiveSmallIntegerField('年齢')
    likes = models.TextField('好きな食べ物', blank=True)
    dislikes = models.TextField('苦手な食べ物', blank=True)
    allergies = models.TextField('アレルギー', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name
