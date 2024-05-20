# Generated by Django 4.2.13 on 2024-05-19 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("prerequisites", models.TextField()),
                ("research_areas", models.JSONField()),
                ("faculty", models.JSONField()),
                ("university", models.CharField(max_length=255)),
                ("ranking", models.IntegerField()),
                ("location", models.CharField(max_length=255)),
            ],
        ),
    ]