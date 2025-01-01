# myapp/management/commands/rewrite_titles.py
from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import Hotel
from myapp.services.gemini_service import GeminiService
import time

class Command(BaseCommand):
    help = 'Rewrite property titles using Gemini API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=2,
            help='Number of hotels to process in each batch'
        )

    def handle(self, *args, **kwargs):
        batch_size = kwargs['batch_size']
        gemini_service = GeminiService()
        
        hotels = Hotel.objects.all()
        total_hotels = hotels.count()
        
        self.stdout.write(f"Found {total_hotels} hotels for title rewriting")

        for i in range(0, total_hotels, batch_size):
            batch = hotels[i:i + batch_size]
            self.stdout.write(f"Processing batch {i//batch_size + 1}")

            for hotel in batch:
                try:
                    with transaction.atomic():
                        new_title = gemini_service.rewrite_property_title(hotel)
                        if new_title:
                            hotel.property_title = new_title
                            hotel.save()
                            self.stdout.write(
                                self.style.SUCCESS(f"Rewrote title for hotel {hotel.id}: {new_title}")
                            )
                        time.sleep(1)  # Rate limiting
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing hotel {hotel.id}: {str(e)}")
                    )