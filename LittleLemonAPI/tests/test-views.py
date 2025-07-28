from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Menu
from .serializers import MenuSerializer
import json


class MenuViewTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user if authentication is required
        self.client = APIClient()
        
        # Create test Menu instances
        self.menu1 = Menu.objects.create(
            title="Pizza Margherita",
            price=12.99,
            inventory=50
        )
        
        self.menu2 = Menu.objects.create(
            title="Pasta Carbonara", 
            price=14.50,
            inventory=30
        )
        
        self.menu3 = Menu.objects.create(
            title="Caesar Salad",
            price=9.99,
            inventory=25
        )

    def test_getall(self):
        """Test retrieving all Menu objects"""
        # Make GET request to menu list endpoint
        # Adjust the URL name based on your urls.py configuration
        url = reverse('menu-list')  # or whatever your URL name is
        response = self.client.get(url)
        
        # Check if request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get all Menu objects from database
        menus = Menu.objects.all()
        
        # Serialize the data
        serializer = MenuSerializer(menus, many=True)
        
        # Assert that serialized data equals response data
        self.assertEqual(response.data, serializer.data)
        
        # Additional assertions
        self.assertEqual(len(response.data), 3)  # Should have 3 menu items
        
        # Check if specific menu items are in response
        menu_titles = [item['title'] for item in response.data]
        self.assertIn("Pizza Margherita", menu_titles)
        self.assertIn("Pasta Carbonara", menu_titles)
        self.assertIn("Caesar Salad", menu_titles)