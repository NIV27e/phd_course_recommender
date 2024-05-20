import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recommender.models import Course

class Command(BaseCommand):
    help = 'Load course data from CSV file into the database'

    def handle(self, *args, **kwargs):
        # Get the project base directory
        base_dir = settings.BASE_DIR
        # Construct the full path to the CSV file
        csv_file_path = os.path.join(base_dir, '..', 'web_scraping', 'phd_courses.csv')

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file_path}'))
            return

        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                description = row['description'] if row['description'].strip() else 'No description available'
                Course.objects.create(
                    title=row['title'],
                    description=description,
                    prerequisites=row.get('prerequisites', 'Not specified'),
                    research_areas=row.get('research_areas', '').strip('][').split(', '),
                    faculty=row.get('faculty', '').strip('][').split(', '),
                    university=row['university'],
                    location=row.get('location', 'Unknown'),
                    ranking=row.get('ranking', 0)  # Provide a default value for ranking
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from CSV'))
