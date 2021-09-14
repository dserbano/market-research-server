from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .models import Task
from utils import Aggregator, Analyzer
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from .serializers import TaskSerializer

@csrf_exempt
@api_view(['GET'])
def all_tasks(request):
    """
        Returns all tasks
    """
    return Response({
        "status": 1,
        "tasks": TaskSerializer(Task.objects.all(), many=True).data
    })

@csrf_exempt
@api_view(['POST'])
def new_task(request):
    """
        Creates a new task
    """
    if request.method == 'POST':
        tasks = list(Task.objects.filter(from_keywords = request.data['keywords']))
        if len(tasks) > 0:
            return Response({"status": 0, "task": None})
        else:
            task = Task(
                from_keywords = request.data['keywords'],
                timestamp = datetime.now(tz=timezone.utc),
                language = request.data['language_code'],
                location = request.data['location_code'],
                keywords = [],
                businesses = [],
                products = [],
                search_volume = [],
                forecasts_search_volume = [],
                clusters_products = []
            )
            task.save()
            return Response({"status": 1, "task": TaskSerializer(task, many=False).data})

@csrf_exempt
@api_view(['POST'])
def execute_task(request):
    """
       Returns keywords, businesses, products, trends associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "keywords": Aggregator.aggregateKeywords(int(request.data['id'])),
            "businesses": Aggregator.aggregateBusinesses(int(request.data['id'])),
            "products": Aggregator.aggregateProducts(int(request.data['id'])),
            "search_volume": Aggregator.aggregateSearchVolume(int(request.data['id'])),
            "forecasts_search_volume": Analyzer.analyzeForecastsSearchVolume(int(request.data['id'])),
            "clusters_products": Analyzer.analyzeClustersProducts(int(request.data['id']))
        })

@csrf_exempt
@api_view(['POST'])
def execute_task_keywords(request):
    """
       Returns a list of keywords associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "keywords": Aggregator.aggregateKeywords(int(request.data['id']))
        })

@csrf_exempt
@api_view(['POST'])
def execute_task_businesses(request):
    """
       Returns a list of businesses associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "businesses": Aggregator.aggregateBusinesses(int(request.data['id']))
        })

@csrf_exempt
@api_view(['POST'])
def execute_task_products(request):
    """
       Returns a list of products associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "products": Aggregator.aggregateProducts(int(request.data['id']))
        })

@csrf_exempt
@api_view(['POST'])
def execute_task_search_volume(request):
    """
       Returns a list of trends associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "search_volume": Aggregator.aggregateSearchVolume(int(request.data['id']))
        })

@csrf_exempt
@api_view(['POST'])
def execute_task_forecasts_search_volume(request):
    """
       Returns a list of trends associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "forecasts_search_volume": Analyzer.analyzeForecastsSearchVolume(int(request.data['id']))
        })

@csrf_exempt
@api_view(['POST'])
def execute_task_clusters_products(request):
    """
       Returns a list of trends associated with the task
    """
    if request.method == 'POST':
        return Response({
            "status": 1,
            "clusters_products": Analyzer.analyzeClustersProducts(int(request.data['id']))
        })