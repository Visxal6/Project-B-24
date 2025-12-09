from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Points, Task
from .models import Event
from django.utils import timezone
import os


User = get_user_model()


class LeaderboardPointsTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='alice', password='pass')
		self.client.login(username='alice', password='pass')

	def test_daily_toggle_awards_and_subtracts_points(self):
		# start with zero points
		pts, _ = Points.objects.get_or_create(user=self.user)
		self.assertEqual(pts.score, 0)

		# toggle first daily task (index 0) -> should award 5 points per daily_tasks.json
		resp = self.client.post(reverse('leaderboard:task_toggle', args=[0]))
		pts.refresh_from_db()
		self.assertEqual(pts.score, 5)

		# toggling again should remove the completion and subtract points back to 0
		resp = self.client.post(reverse('leaderboard:task_toggle', args=[0]))
		pts.refresh_from_db()
		self.assertEqual(pts.score, 0)

	def test_weekly_toggle_requires_and_stores_proof_and_awards_points(self):
		pts, _ = Points.objects.get_or_create(user=self.user)
		self.assertEqual(pts.score, 0)

		# posting without a file should not create a Task and not change points
		resp = self.client.post(reverse('leaderboard:weekly_toggle', args=[0]))
		pts.refresh_from_db()
		self.assertEqual(pts.score, 0)

		# post with an uploaded image file
		file_path = os.path.join(os.path.dirname(__file__), 'test_data', 'example.jpg')
		# create a small dummy image in-memory if it doesn't exist
		image_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
		upload = SimpleUploadedFile('proof.gif', image_data, content_type='image/gif')
		resp = self.client.post(reverse('leaderboard:weekly_toggle', args=[0]), {'proof': upload})

		pts.refresh_from_db()
		# weekly_tasks.json first entry is 30 points; ensure Points updated
		self.assertEqual(pts.score, 30)

		# ensure a Task was created and has an image
		task = Task.objects.filter(user=self.user, completed=True, title__icontains='Zero-waste').first()
		self.assertIsNotNone(task)
		self.assertTrue(bool(task.image))


	def test_cio_can_create_event_and_detail_page(self):
		# create CIO user and profile
		cio = User.objects.create_user(username='cio', password='pass')
		from users.models import Profile
		Profile.objects.create(user=cio, role='cio')
		self.client.logout()
		self.client.login(username='cio', password='pass')

		start = timezone.now()
		start_val = start.strftime('%Y-%m-%dT%H:%M')
		resp = self.client.post(reverse('leaderboard:event_create'), {
			'title': 'Test Event',
			'description': 'This is a sample event',
			'start_at': start_val,
			'location': 'Test Hall'
		})
		# should redirect back to events list
		self.assertEqual(resp.status_code, 302)
		e = Event.objects.filter(title='Test Event').first()
		self.assertIsNotNone(e)

		# events list should include this event
		resp = self.client.get(reverse('leaderboard:events_list'))
		self.assertContains(resp, 'Test Event')

		# detail page should render description
		resp = self.client.get(reverse('leaderboard:event_detail', args=[e.id]))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'This is a sample event')


	def test_non_cio_cannot_create_event(self):
		# alice user (non-cio) should be prevented
		resp = self.client.post(reverse('leaderboard:event_create'), {
			'title': 'Nope', 'start_at': timezone.now().strftime('%Y-%m-%dT%H:%M')
		})
		# redirected to events_list and no event created
		self.assertEqual(resp.status_code, 302)
		self.assertFalse(Event.objects.filter(title='Nope').exists())

