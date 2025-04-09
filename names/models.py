from django.db import models


class NameData(models.Model):
    name = models.CharField(max_length=100, unique=True)
    count = models.IntegerField()
    country = models.JSONField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Данные'
        verbose_name_plural = 'Данные'