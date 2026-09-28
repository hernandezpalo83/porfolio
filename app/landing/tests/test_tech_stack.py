"""Tests del stack tecnológico en la experiencia y de los casos de éxito con modal."""
import datetime

from django.contrib import admin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from app.landing.models import Experience, Project, Technology
from app.landing.templatetags.ui import plain_text


class TechnologyModelTests(TestCase):
    def test_name_is_unique_ignoring_case(self):
        Technology.objects.create(name='Django')
        with self.assertRaises(ValidationError):
            Technology(name=' django ').full_clean()

    def test_registered_in_admin(self):
        self.assertIn(Technology, admin.site._registry)
        self.assertIn('technologies', admin.site._registry[Experience].filter_horizontal)


class TechStackRenderingTests(TestCase):
    fixtures = ['test_landing.json']

    def setUp(self):
        cache.clear()
        self.exp = Experience.objects.create(company='ACME', position='TPM',
                                             start_date=datetime.date(2020, 1, 1))
        self.exp.technologies.add(Technology.objects.create(name='PostgreSQL'))
        self.project = Project.objects.create(title='Caso X', description='<p>Largo</p>' * 50,
                                              resumen='Resumen corto del caso')

    def test_experience_shows_stack_badges(self):
        resp = self.client.get(reverse('landing:index'))
        self.assertContains(resp, 'aria-label="Stack tecnológico"')
        self.assertContains(resp, '<li>PostgreSQL</li>', html=False)

    def test_changing_stack_invalidates_home_cache(self):
        self.client.get(reverse('landing:index'))
        self.exp.technologies.add(Technology.objects.create(name='Kubernetes'))
        self.assertContains(self.client.get(reverse('landing:index')), 'Kubernetes')

    def test_project_card_uses_summary_and_dialog(self):
        resp = self.client.get(reverse('landing:index'))
        self.assertContains(resp, 'Resumen corto del caso')
        self.assertContains(resp, f'data-dialog-open="case-{self.project.pk}"')
        self.assertContains(resp, f'<dialog id="case-{self.project.pk}"')


class PlainTextFilterTests(TestCase):
    def test_keeps_word_boundaries(self):
        self.assertEqual(plain_text('<p>Uno<br>dos</p><ul><li>tres</li></ul>&amp;'), 'Uno dos tres &')


class PortfolioFilterTests(TestCase):
    def test_categories_are_merged_ignoring_case(self):
        from app.landing.portfolio import build_portfolio
        a = Project.objects.create(title='Blog Engine', categoria='DJANGO, Web')
        b = Project.objects.create(title='Gym', categoria='Django, AWS')
        projects, filters = build_portfolio([a, b])
        self.assertEqual(filters[0], {'key': 'django', 'label': 'Django', 'count': 2})
        self.assertIn({'key': 'aws', 'label': 'AWS', 'count': 1}, filters)
        self.assertEqual([t['label'] for t in projects[0].tags], ['Django', 'Web'])
        self.assertEqual(projects[0].initials, 'BE')

    def test_home_renders_filter_chips(self):
        cache.clear()
        Project.objects.create(title='A', categoria='Django')
        Project.objects.create(title='B', categoria='Python')
        resp = self.client.get(reverse('landing:index'))
        self.assertContains(resp, 'data-filter="django"')
        self.assertContains(resp, 'data-tags="python "')
