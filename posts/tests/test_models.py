from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='testuser')
        cls.group = Group.objects.create(id=1, title='Название', slug='слаг', description='описание')
        cls.post = Post.objects.create(id=1, text='Текст', pub_date='дата', author=cls.author, group=cls.group)

    def test_post_verbose_name(self):
        """verbose_name для post."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).verbose_name, expected)

    def test_post_help_texts(self):
        """help_text для post."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите текст поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text, expected)

    def test_group_verbose_name(self):
        """verbose_name для group."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(group._meta.get_field(value).verbose_name, expected)

    def test_group_help_texts(self):
        """help_text для group."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(group._meta.get_field(value).help_text, expected)

    def test_object_name_is_text_fild_post(self):
        """В поле __str__  объекта post записано значение поля post.text."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_object_name_is_title_fild_group(self):
        """В поле __str__  объекта group записано значение поля group.text."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
