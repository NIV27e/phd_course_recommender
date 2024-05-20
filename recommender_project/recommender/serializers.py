from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'prerequisites', 'research_areas', 'faculty', 'university', 'ranking', 'location']
