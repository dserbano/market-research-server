from django.contrib import admin
from tasks.models import Task

class TaskSettings(admin.ModelAdmin):
    list_display = ("id", "from_keywords", "language", "location", "timestamp", "keywords", "businesses", "products", "search_volume", "forecasts_search_volume", "clusters_products")


admin.site.register(Task, TaskSettings)

