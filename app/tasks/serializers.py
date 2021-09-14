from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "from_keywords", "language", "location", "timestamp", "keywords", "businesses", "products", "search_volume", "forecasts_search_volume", "clusters_products")
