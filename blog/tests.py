from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import DiaryPage


class DiaryPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='secret123',
        )

    def test_save_page_from_home_view(self):
        self.client.login(username='tester', password='secret123')

        response = self.client.post(
            reverse('home'),
            {'action': 'save', 'written_date': '2026-07-01', 'page': 'My first diary entry'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(DiaryPage.objects.filter(written_date='2026-07-01').exists())

    def test_search_by_date_filters_pages(self):
        DiaryPage.objects.create(written_date='2026-07-01', search_date='2026-07-01', page='One')
        DiaryPage.objects.create(written_date='2026-07-02', search_date='2026-07-02', page='Two')

        self.client.login(username='tester', password='secret123')

        response = self.client.post(
            reverse('home'),
            {'action': 'search', 'search_date': '2026-07-01'},
        )

        self.assertContains(response, 'One')
        self.assertNotContains(response, 'Two')
