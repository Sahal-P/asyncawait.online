from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import User

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")  # Replace "register" with your actual view name
        self.login_url = reverse("login")  # Replace "login" with your actual view name
        self.logout_url = reverse("logout")  # Replace "logout" with your actual view name
        
        # Create a test user
        self.test_user = User.objects.create_user(
         email="testuser@gmail.com",  username="testuser", phone_number="1234567890", password="testpassword"
        )
    
    def test_register_api(self):
        data = {
            "username": "newuser",
            "email": "newuser@gmail.com",
            "phone_number": "+919876543210",
            "password": "newpassword",
            "confirm_password": "newpassword",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_api(self):
        data = {
            "phone_number": "1234567890",
            "password": "testpassword",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_api(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

# Run the tests