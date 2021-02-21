from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    def test_home_desired_location(self):
        # Страница / доступна любому пользователю.
        response = self.guest_client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_home_correct_template(self):
        # Проверка шаблона для адреса /.
        response = self.guest_client.get(reverse("index"))
        self.assertTemplateUsed(response, 'posts/index.html')


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(username='username')
        cls.group = Group.objects.create(title='Название', slug='slug', description='описание')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.test_author,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = get_user_model().objects.create_user(username='lala')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.editor_client = Client()
        self.editor_client.force_login(PostURLTests.test_author)

    def test_urls_exists_at_desired_location_for_auth(self):
        # URL-адрес работает для авториз пользователя."""
        url_names = {
            reverse('group_posts', args={'slug'}): 200,
            reverse('new_post'): 200,
            reverse('profile', args={'username'}): 200,
            reverse('post', args={'username', 1}): 200,
        }
        for reverse_name, result_code in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, result_code)

    def test_urls_exists_at_desired_location_for_client(self):
        # URL-адрес работает для неавториз пользователя."""
        url_names = {
            reverse('group_posts', args={'slug'}): 200,
            reverse('new_post'): 302,
            reverse('profile', args={'username'}): 200,
            reverse('post', args={'username', 1}): 200,
        }

        for reverse_name, result_code in url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, result_code)

    def test_urls_exists_at_desired_location_for_edit_author(self):
        response = self.editor_client.get(reverse('post_edit', args={'username', 1}))
        self.assertEqual(response.status_code, 200)

    def test_urls_exists_at_desired_location_for_edit_guest(self):
        response = self.guest_client.get(reverse('post_edit', args={'username', 1}))
        self.assertEqual(response.status_code, 302)

    def test_urls_exists_at_desired_location_for_edit_notauthor(self):
        response = self.authorized_client.get(reverse('post_edit', args={'username', 1}))
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        # URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('group_posts', args={'slug'}): 'posts/group.html',
            reverse('new_post'): 'posts/new.html',
            reverse('post_edit', args={'username', 1}): 'posts/new.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.editor_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_redirect_for_guest_when_edit(self):
        response = self.guest_client.get(reverse('post_edit', args={'username', 1}), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/username/1/edit/')

    def test_redirect_for_client_notauthor_when_edit(self):
        response = self.authorized_client.get(reverse('post_edit', args={'username', 1}), follow=True)
        self.assertRedirects(response, '/username/1/')
