# myapp/management/commands/generate_descriptions.py
from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import Hotel
from myapp.services.gemini_service import GeminiService
import time

class Command(BaseCommand):
    help = 'Generate descriptions for hotels using Gemini API'

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
        
        # Get hotels without descriptions
        hotels = Hotel.objects.filter(description__isnull=True)
        total_hotels = hotels.count()
        
        self.stdout.write(f"Found {total_hotels} hotels without descriptions")

        for i in range(0, total_hotels, batch_size):
            batch = hotels[i:i + batch_size]
            self.stdout.write(f"Processing batch {i//batch_size + 1}")

            for hotel in batch:
                try:
                    with transaction.atomic():
                        property_data = {
                            'property_title': hotel.property_title,
                            'city_name': hotel.city_name,
                            'room_type': hotel.room_type,
                            'price': str(hotel.price),
                            'rating': str(hotel.rating)
                        }
                        
                        description = gemini_service.generate_property_description(property_data)
                        
                        if description:
                            hotel.description = description
                            hotel.save()
                            self.stdout.write(
                                self.style.SUCCESS(f"Generated description for: {hotel.property_title}")
                            )
                        time.sleep(1)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing hotel {hotel.id}: {str(e)}")
                    )