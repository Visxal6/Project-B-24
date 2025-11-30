from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from leaderboard.models import Points
from .models import Profile


User = get_user_model()


class CIOLeaderboardTests(TestCase):
    def setUp(self):
        # create multiple users with profiles and points
        self.cio = User.objects.create_user(username='cio-user', password='pass')
        self.user1 = User.objects.create_user(username='alice', password='pass')
        self.user2 = User.objects.create_user(username='bob', password='pass')

        Profile.objects.create(user=self.cio, role='cio')
        Profile.objects.create(user=self.user1, role='student')
        Profile.objects.create(user=self.user2, role='cio')

        # assign points
        Points.objects.create(user=self.cio, score=10)
        Points.objects.create(user=self.user1, score=20)
        Points.objects.create(user=self.user2, score=30)

    def test_cio_leaderboard_only_contains_cio_profiles(self):
        resp = self.client.get(reverse('dashboard'))
        # dashboard should include cio_leaderboard context
        self.assertEqual(resp.status_code, 200)
        cio_list = resp.context['cio_leaderboard']
        # all entries user should be a CIO (profile.role == 'cio')
        for entry in cio_list:
            profile = Profile.objects.filter(user=entry['user']).first()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.role, 'cio')
from django.test import TestCase

# Create your tests here.
