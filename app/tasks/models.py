from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    from_keywords = models.CharField(max_length=1000)
    language = models.CharField(max_length=1000)
    location = models.CharField(max_length=1000)
    timestamp = models.DateTimeField()
    keywords = models.JSONField()
    businesses = models.JSONField()
    products = models.JSONField()
    search_volume = models.JSONField()
    forecasts_search_volume = models.JSONField()
    clusters_products = models.JSONField()

    class Meta:
        db_table = "tasks"
        verbose_name = "Task"
        verbose_name_plural = "Tasks"





