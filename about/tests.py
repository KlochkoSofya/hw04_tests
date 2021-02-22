from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени static_pages:about, доступен."""
        about_list = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200
        }
        for reverse_name, expected in about_list.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, expected)

    def test_about_page_uses_correct_template(self):

        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
