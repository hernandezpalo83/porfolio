from django.test import TestCase
from django.contrib.auth.models import User
from app.analytics.models import PageView, SessionTracker


class AnalyticsModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_pageview_creation(self):
        pv = PageView.objects.create(
            path='/test/',
            method='GET',
            country='ES',
            device='Desktop',
            session_id='test-session-123'
        )
        self.assertEqual(pv.path, '/test/')
        self.assertEqual(pv.country, 'ES')

    def test_session_tracker_creation(self):
        st = SessionTracker.objects.create(
            session_id='test-session-456',
            country='ES',
            device='Mobile',
            first_page='/home/',
            last_page='/blog/',
            page_count=5,
            is_bounce=False
        )
        self.assertEqual(st.page_count, 5)
        self.assertFalse(st.is_bounce)
