# myapp/management/commands/generate_summaries.py

from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import Hotel, PropertySummary
from myapp.services.gemini_service import GeminiService
import time

class Command(BaseCommand):
    help = 'Generate summaries for hotels using Gemini API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=2,
            help='Number of hotels to process in each batch'
        )

    def handle(self, *args, **kwargs):
        batch_size = kwargs['batch_size']
        gemini_service = GeminiService()  # 2 minute timeout
        
        # Modified query to handle hotels with descriptions
        hotels = Hotel.objects.filter(description__isnull=False).exclude(summaries__isnull=False)
        total_hotels = hotels.count()
        
        self.stdout.write(f"Found {total_hotels} hotels without summaries")

        for i in range(0, total_hotels, batch_size):
            batch = hotels[i:i + batch_size]
            self.stdout.write(f"Processing batch {i//batch_size + 1}")

            for hotel in batch:
                try:
                    with transaction.atomic():
                        property_data = {
                            'property_title': hotel.property_title,
                            'city_name': hotel.city_name,
                            'price': f"{hotel.price:.2f}" if hotel.price is not None else "N/A",
                            'rating': f"{hotel.rating:.1f}" if hotel.rating is not None else "N/A",
                            'description': hotel.description or "Not available"
                        }
                        
                        summary = gemini_service.generate_property_summary(property_data)
                        
                        if summary:
                            PropertySummary.objects.create(
                                property=hotel,
                                summary=summary
                            )
                            self.stdout.write(
                                self.style.SUCCESS(f"Generated summary for: {hotel.property_title}")
                            )
                        time.sleep(1)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing hotel {hotel.id}: {str(e)}")
                    )