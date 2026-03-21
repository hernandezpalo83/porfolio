"""
Tests de modelos para app.landing.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from app.landing.models import (
    CompanyCollaboration, Contacto, Experience, Metric, Skill,
)


class SkillModelTests(TestCase):

    def test_clean_score_above_100_raises(self):
        s = Skill(name="Test", score=101)
        with self.assertRaises(ValidationError):
            s.clean()

    def test_clean_score_below_0_raises(self):
        s = Skill(name="Test", score=-1)
        with self.assertRaises(ValidationError):
            s.clean()

    def test_clean_valid_score_passes(self):
        s = Skill(name="Test", score=90)
        try:
            s.clean()
        except ValidationError:
            self.fail("clean() raised for valid score")

    def test_str_includes_name_and_score(self):
        s = Skill.objects.create(name="Python", score=95)
        self.assertIn("Python", str(s))
        self.assertIn("95", str(s))


class ExperienceModelTests(TestCase):

    def test_clean_end_before_start_raises(self):
        from datetime import date
        e = Experience(
            company="Acme", position="Dev",
            start_date=date(2020, 1, 1), end_date=date(2019, 1, 1)
        )
        with self.assertRaises(ValidationError):
            e.clean()

    def test_clean_no_end_date_passes(self):
        from datetime import date
        e = Experience(
            company="Acme", position="Dev",
            start_date=date(2020, 1, 1), end_date=None
        )
        try:
            e.clean()
        except ValidationError:
            self.fail("clean() raised for open-ended experience")


class MetricModelTests(TestCase):

    def test_clean_negative_value_raises(self):
        m = Metric(value=-1, title="Test", description="D")
        with self.assertRaises(ValidationError):
            m.clean()

    def test_get_percent_max_100(self):
        m = Metric(value=200, title="Test", description="D")
        self.assertEqual(m.get_percent(), 100)

    def test_get_percent_under_100(self):
        m = Metric(value=75, title="Test", description="D")
        self.assertEqual(m.get_percent(), 75)

    def test_str_includes_value_and_title(self):
        m = Metric.objects.create(value=10, title="Proyectos", description="D")
        self.assertIn("10", str(m))
        self.assertIn("Proyectos", str(m))


class ContactoModelTests(TestCase):

    def test_default_leido_is_false(self):
        c = Contacto.objects.create(
            nombre="Test", email="t@t.com", asunto="Asunto", mensaje="Mensaje largo"
        )
        self.assertFalse(c.leido)

    def test_str_includes_nombre_and_asunto(self):
        c = Contacto.objects.create(
            nombre="Javier", email="j@j.com", asunto="Consulta", mensaje="Texto"
        )
        self.assertIn("Javier", str(c))
        self.assertIn("Consulta", str(c))

    def test_ordering_desc_by_fecha_envio(self):
        Contacto.objects.create(nombre="A", email="a@a.com", asunto="A", mensaje="A")
        Contacto.objects.create(nombre="B", email="b@b.com", asunto="B", mensaje="B")
        contactos = list(Contacto.objects.values_list('nombre', flat=True))
        # El más reciente (B) debe ir primero
        self.assertEqual(contactos[0], "B")


class CompanyCollaborationModelTests(TestCase):

    def test_logo_cdn_url_with_leading_slash(self):
        from django.test import override_settings
        with override_settings(BRAND_ASSETS_URL='https://cdn.example.com'):
            c = CompanyCollaboration(name="Acme", logo="/logos/acme.webp")
            self.assertEqual(c.logo_cdn_url, 'https://cdn.example.com/logos/acme.webp')

    def test_logo_cdn_url_empty_logo(self):
        c = CompanyCollaboration(name="Acme", logo="")
        self.assertEqual(c.logo_cdn_url, "")

    def test_str_is_name(self):
        c = CompanyCollaboration.objects.create(name="Empresa Test")
        self.assertEqual(str(c), "Empresa Test")
