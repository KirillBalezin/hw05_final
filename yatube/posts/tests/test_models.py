from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class MyModel():
    TEXT_LENGTH = 15


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
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        mapping = {
            self.post.text[:MyModel.TEXT_LENGTH]: str(self.post),
            self.group.title: str(self.group),
            self.comment.text[:MyModel.TEXT_LENGTH]: str(self.comment)
        }
        for expected_object_name, value in mapping.items():
            with self.subTest(object=object):
                self.assertEqual(expected_object_name, value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        models_verboses = {
            Post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа'
            },
            Group: {
                'title': 'Название',
                'description': 'Описание'
            },
            Follow: {
                'author': 'Автор',
                'user': 'Пользователь'
            },
            Comment: {
                'post': 'Пост',
                'author': 'Автор',
                'text': 'Текст комментария',
                'created': 'Дата публикации'
            }
        }
        for model, expected_value in models_verboses.items():
            for field, value in expected_value.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        value
                    )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        models_help_texts = {
            Post: {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
            },
            Group: {
                'title': 'Введите название группы',
                'description': 'Напишите описание группы'
            },
            Comment: {
                'text': 'Введите текст комментария'
            }
        }
        for model, expected_value in models_help_texts.items():
            for field, value in expected_value.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text, value)
