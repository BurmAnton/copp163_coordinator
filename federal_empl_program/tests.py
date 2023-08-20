from django.test import TestCase, Client

from users.models import User

# Create your tests here.
class IndexTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    
    def test_view(self):
        # Issue a GET request.
        response = self.client.get("")

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 302)


class ImportExpressTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        User.objects.create_user(email='testuser@test.com', password='12345')
        self.client = Client()
        
    def test_view(self):
        # Issue a GET request.
        self.client.login(username='testuser@test.com', password='12345') 
        response = self.client.get("/import/express/")

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)