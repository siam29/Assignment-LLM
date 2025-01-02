from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch, MagicMock
from io import StringIO
from myapp.models import Hotel

class TestGenerateDescriptionsCommand(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test hotels
        self.hotel1 = Hotel.objects.create(
            property_title="Test Hotel 1",
            city_name="Test City",
            room_type="Deluxe",
            price=100.00,
            rating=4.5,
            description=None
        )
        
        self.hotel2 = Hotel.objects.create(
            property_title="Test Hotel 2",
            city_name="Test City",
            room_type="Standard",
            price=80.00,
            rating=4.0,
            description=None
        )
        
        self.hotel_with_description = Hotel.objects.create(
            property_title="Test Hotel 3",
            city_name="Test City",
            room_type="Suite",
            price=200.00,
            rating=4.8,
            description="Existing description"
        )
        
        # Create StringIO object to capture command output
        self.out = StringIO()
    
    def test_generate_descriptions_success(self):
        """Test successful generation of descriptions"""
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            # Configure mock
            mock_instance = mock_gemini.return_value
            mock_instance.generate_property_description.return_value = "Generated description"
            
            # Call command
            call_command('generate_descriptions', stdout=self.out)
            
            # Assert output messages
            output = self.out.getvalue()
            self.assertIn("Found 2 hotels without descriptions", output)
            self.assertIn("Generated description for: Test Hotel 1", output)
            self.assertIn("Generated description for: Test Hotel 2", output)
            
            # Assert database updates
            self.hotel1.refresh_from_db()
            self.hotel2.refresh_from_db()
            self.assertEqual(self.hotel1.description, "Generated description")
            self.assertEqual(self.hotel2.description, "Generated description")
    
    def test_batch_processing(self):
        """Test processing hotels in batches"""
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            mock_instance = mock_gemini.return_value
            mock_instance.generate_property_description.return_value = "Generated description"
            
            # Call command with batch size 1
            call_command('generate_descriptions', batch_size=1, stdout=self.out)
            
            output = self.out.getvalue()
            self.assertIn("Processing batch 1", output)
            self.assertIn("Processing batch 2", output)
    
    def test_error_handling(self):
        """Test handling of API errors"""
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            mock_instance = mock_gemini.return_value
            mock_instance.generate_property_description.side_effect = Exception("API Error")
            
            # Call command
            call_command('generate_descriptions', stdout=self.out)
            
            # Assert error message
            output = self.out.getvalue()
            self.assertIn("Error processing hotel", output)
            self.assertIn("API Error", output)
            
            # Assert no changes to database
            self.hotel1.refresh_from_db()
            self.assertIsNone(self.hotel1.description)
    
    def test_skip_existing_descriptions(self):
        """Test that hotels with existing descriptions are skipped"""
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            mock_instance = mock_gemini.return_value
            mock_instance.generate_property_description.return_value = "New description"
            
            # Call command
            call_command('generate_descriptions', stdout=self.out)
            
            # Assert existing description wasn't changed
            self.hotel_with_description.refresh_from_db()
            self.assertEqual(self.hotel_with_description.description, "Existing description")
            
            # Assert correct count in output
            output = self.out.getvalue()
            self.assertIn("Found 2 hotels without descriptions", output)
    
    @patch('time.sleep')
    def test_rate_limiting(self, mock_sleep):
        """Test rate limiting between API calls"""
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            mock_instance = mock_gemini.return_value
            mock_instance.generate_property_description.return_value = "Generated description"
            
            # Call command
            call_command('generate_descriptions', batch_size=1, stdout=self.out)
            
            # Assert sleep was called between API calls
            self.assertTrue(mock_sleep.called)
            mock_sleep.assert_called_with(1)
    
    def test_transaction_integrity(self):
        """Test transaction integrity when error occurs"""
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            mock_instance = mock_gemini.return_value
            # First call succeeds, second fails
            mock_instance.generate_property_description.side_effect = [
                "Success description",
                Exception("API Error")
            ]
            
            # Call command
            call_command('generate_descriptions', batch_size=1, stdout=self.out)
            
            # Assert first hotel was updated
            self.hotel1.refresh_from_db()
            self.assertEqual(self.hotel1.description, "Success description")
            
            # Assert second hotel wasn't updated
            self.hotel2.refresh_from_db()
            self.assertIsNone(self.hotel2.description)
    
    def test_empty_hotel_list(self):
        """Test behavior when no hotels need processing"""
        # Delete all hotels without descriptions
        Hotel.objects.filter(description__isnull=True).delete()
        
        with patch('myapp.services.gemini_service.GeminiService') as mock_gemini:
            mock_instance = mock_gemini.return_value
            
            # Call command
            call_command('generate_descriptions', stdout=self.out)
            
            # Assert output
            output = self.out.getvalue()
            self.assertIn("Found 0 hotels without descriptions", output)
            
            # Assert no API calls were made
            mock_instance.generate_property_description.assert_not_called()