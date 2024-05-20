from django.urls import path
from .views import recommend_courses

urlpatterns = [
    path('recommend/<int:course_id>/', recommend_courses, name='recommend_courses'),
]
