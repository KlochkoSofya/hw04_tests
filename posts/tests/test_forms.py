from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django.contrib.auth import get_user_model

User = get_user_model()


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных

        cls.group = Group.objects.create(title='Группа', slug='test-slug')
        cls.post = Post.objects.create(
            text='Текст',
            author = User.objects.create_user(username='StasBasov'),
            group = cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StanislavaBasova')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        # Подсчитаем количество записей в post
        posts_count = Post.objects.count()
        form_data = {
            'author': self.authorized_client,
            'text': 'Текст',
            'group': Group.objects.get(slug ='test-slug').id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(reverse('new_post'), data=form_data, follow=True)
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):

        form_data={'text':'Отредактированный текст'}
        response = self.authorized_client.post(
            reverse('post_edit', args = [self.user.username, self.post.id]), data = form_data, follow=True)
        self.assertEqual(Post.objects.filter(id=self.post.id).last().text, 'Отредактированный текст')
        