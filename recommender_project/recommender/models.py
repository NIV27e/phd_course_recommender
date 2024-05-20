from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    prerequisites = models.TextField()
    research_areas = models.JSONField()
    faculty = models.JSONField()
    university = models.CharField(max_length=255)
    ranking = models.IntegerField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.title

