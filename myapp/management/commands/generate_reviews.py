# myapp/management/commands/generate_reviews.py

from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import Hotel, PropertyReview
from myapp.services.gemini_service import GeminiService
import time

class Command(BaseCommand):
    help = 'Generate reviews for hotels using Gemini API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=2,
            help='Number of hotels to process in each batch'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regenerate reviews even for hotels that already have them'
        )

    def handle(self, *args, **kwargs):
        batch_size = kwargs['batch_size']
        force = kwargs['force']
        gemini_service = GeminiService() 
        
        # Get hotels without reviews or all hotels if force is True
        if force:
            hotels = Hotel.objects.all()
        else:
            hotels = Hotel.objects.exclude(reviews__isnull=False)
            
        total_hotels = hotels.count()
        
        self.stdout.write(f"Found {total_hotels} hotels to process")

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
                            'rating': f"{hotel.rating:.1f}" if hotel.rating is not None else "3.0"  # Default rating
                        }
                        
                        rating, review = gemini_service.generate_property_review(property_data)
                        
                        if rating is not None and review:
                            if force:
                                # Delete existing reviews if force is True
                                hotel.reviews.all().delete()
                                
                            PropertyReview.objects.create(
                                property=hotel,
                                rating=rating,
                                review=review
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Generated review for: {hotel.property_title}\n"
                                    f"Rating: {rating}\n"
                                    f"Review: {review[:100]}..."
                                )
                            )
                        time.sleep(1)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing hotel {hotel.id}: {str(e)}")
                    )