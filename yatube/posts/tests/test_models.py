from django.test import TestCase

from ..models import Group, Post, User, Comment

POST_LENGHT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        mapping = {
            self.post.text[:POST_LENGHT]: str(self.post),
            self.group.title: str(self.group),
        }
        for expected_object_name, value in mapping.items():
            with self.subTest(object=object):
                self.assertEqual(expected_object_name, value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_comment(self):
        """verbose_name в поле комментария совпадает с ожидаемым."""
        self.assertEqual(
            Comment._meta.get_field('text').verbose_name, 'Текст комментария'
        )

    def test_help_text_comment(self):
        """help_text в поле комментария совпадает с ожидаемым."""
        self.assertEqual(
            Comment._meta.get_field('text').help_text,
            'Введите текст комментария'
        )
