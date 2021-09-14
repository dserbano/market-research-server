"""market_research_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tasks.views import all_tasks, new_task, execute_task, execute_task_search_volume, execute_task_products, execute_task_keywords, execute_task_businesses, execute_task_forecasts_search_volume, execute_task_clusters_products


urlpatterns = [
    path("", execute_task),
    path("all_tasks/", all_tasks, name="all_tasks"),
    path("new_task/", new_task, name="new_task"),
    path("execute_task/", execute_task, name="execute_task"),
    path("execute_task_keywords/", execute_task_keywords, name="execute_task_keywords"),
    path("execute_task_products/", execute_task_products, name="execute_task_products"),
    path("execute_task_businesses/", execute_task_businesses, name="execute_task_businesses"),
    path("execute_task_search_volume/", execute_task_search_volume, name="execute_task_search_volume"),
    path("execute_task_forecasts_search_volume/", execute_task_forecasts_search_volume, name="execute_task_forecasts_search_volume"),
    path("execute_task_clusters_products/", execute_task_clusters_products, name="execute_task_clusters_products"),
    path("admin/", admin.site.urls),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
