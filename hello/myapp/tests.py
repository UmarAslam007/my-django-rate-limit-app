
# Create your tests here.

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
import redis

GROUP_LIMITS = {
    'Gold': 10,
    'Silver': 5,
    'Bronze': 2,
    'Unauthenticated': 1
}

class RateLimitMiddlewareGroupTests(TestCase):
    def setUp(self):
         # Connect to Redis used by your middleware
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        # Clear all keys related to rate limit before each test
        self.redis_client.flushdb()

        # Create groups
        for group_name in ['Gold', 'Silver', 'Bronze']:
            Group.objects.get_or_create(name=group_name)

        # Create users for each group
        self.gold_user = User.objects.create_user('golduser', password='testpass')
        self.silver_user = User.objects.create_user('silveruser', password='testpass')
        self.bronze_user = User.objects.create_user('bronzeuser', password='testpass')

        # Assign groups
        self.gold_user.groups.add(Group.objects.get(name='Gold'))
        self.silver_user.groups.add(Group.objects.get(name='Silver'))
        self.bronze_user.groups.add(Group.objects.get(name='Bronze'))

        # Create clients and login users
        self.gold_client = Client()
        self.silver_client = Client()
        self.bronze_client = Client()
        self.anon_client = Client()  # unauthenticated

        self.gold_client.login(username='golduser', password='testpass')
        self.silver_client.login(username='silveruser', password='testpass')
        self.bronze_client.login(username='bronzeuser', password='testpass')

    def _test_rate_limit(self, client, limit):
        for i in range(limit):
            response = client.get('/')
            self.assertNotEqual(response.status_code, 429, f"Request {i+1} should NOT be rate limited")

        # The next request should get rate limited
        response = client.get('/')
        self.assertEqual(response.status_code, 429, f"Request {limit+1} should be rate limited")

    def test_gold_user_limit(self):
        self._test_rate_limit(self.gold_client, GROUP_LIMITS['Gold'])

    def test_silver_user_limit(self):
        self._test_rate_limit(self.silver_client, GROUP_LIMITS['Silver'])

    def test_bronze_user_limit(self):
        self._test_rate_limit(self.bronze_client, GROUP_LIMITS['Bronze'])

    def test_unauthenticated_user_limit(self):
        # No login for anon client
        self._test_rate_limit(self.anon_client, GROUP_LIMITS['Unauthenticated'])
