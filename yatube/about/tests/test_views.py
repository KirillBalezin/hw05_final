from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus


class StaticViewsTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имен, доступны."""
        names = (
            'about:author',
            'about:tech',
        )
        for name in names:
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:author и about:tech
        применяется правильные шаблоны"""
        template_urls_name = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in template_urls_name.items():
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
