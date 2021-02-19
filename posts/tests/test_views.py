from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group

User = get_user_model()


class PostViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.test_author = User.objects.create_user(username='username')
        cls.group_1 = Group.objects.create(title='Группа-1', slug='test-slug-1')
        cls.group_2 = Group.objects.create(title='Группа-2', slug='test-slug-2')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.test_author,
            group=cls.group_1
        )
        all_posts = []
        for i in range(0, 12, 1):
            all_posts.append(Post(text='Тестовый пост' + str(i), author=cls.test_author))
        Post.objects.bulk_create(all_posts)

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StanislavaBasova')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.editor_client = Client()
        self.editor_client.force_login(PostViewsTests.test_author)

    def test_paginator(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_correct_template_views(self):

        templates_pages_names = {
            'posts/index.html': reverse('index'),
            'posts/new.html': reverse('new_post'),
            'posts/group.html': (reverse('group_posts', args={'test-slug-1'}))
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_show_correct_context(self):
        response = self.guest_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_author_0.username, 'username')
        self.assertEqual(post_group_0.title, 'Группа-1')

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('group_posts', args={'test-slug-1'}))
        test_group_title_0 = response.context.get('group').title
        test_group_slug_0 = response.context.get('group').slug
        self.assertEqual(test_group_title_0, 'Группа-1')
        self.assertEqual(test_group_slug_0, 'test-slug-1')

    def test_new_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
         }

        for fiels_name, expected in form_fields.items():
            with self.subTest(value=fiels_name):
                form_field = response.context.get('form').fields.get(fiels_name)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_in_correct_group(self):

        group_list = {
            'correct_group': reverse('group_posts', args={'test-slug-1'}),
            'wrong_group': reverse('group_posts', args={'test-slug-2'})
        }

        for the_group, reverse_name in group_list.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                post_in_group = response.context.get('page')
                if the_group == 'correct_group':
                    self.assertIn(self.post, post_in_group)
                else:
                    self.assertNotIn(self.post, post_in_group)

    def test_main_page_shows_post(self):
        response = self.authorized_client.get(reverse("index"))
        main_page = response.context.get('page')
        self.assertIn(self.post, main_page)

    def test_edit_page_show_correct_context(self):
        response = self.editor_client.get('/username/1/edit/')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for fiels_name, expected in form_fields.items():
            with self.subTest(value=fiels_name):
                form_field = response.context.get('form').fields.get(fiels_name)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.guest_client.get(reverse('profile', args={'username'}))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_author_0.username, 'username')
        self.assertEqual(post_group_0.title, 'Группа-1')

    def test_post_page_show_correct_context(self):
        response = self.guest_client.get('/username/1/')
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author
        post_group = response.context.get('post').group
        self.assertEqual(post_text, 'Текст')
        self.assertEqual(post_author.username, 'username')
        self.assertEqual(post_group.title, 'Группа-1')

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
