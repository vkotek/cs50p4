from django.core.management.base import BaseCommand, CommandError

from restaurants.models import Restaurant, Menu

class Command(BaseCommand):
    help = 'Scrapes daily menu from restaurants'

    def add_arguments(self, parser):
        parser.add_argument('--restaurant_ids', type=int)

    def handle(self, *args, **options):
        for restaurant in Restaurant.objects.all():
            self.stdout.write(f"Scraping {restaurant.name}")