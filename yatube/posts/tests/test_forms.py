import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from http import HTTPStatus

from ..models import Comment, Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

CREATE_POST_URL = reverse('posts:post_create')

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
uploaded = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='test_group2',
            slug='test_slug2',
            description='Тестовое описание2'
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.PROFILE_URL = reverse(
            'posts:profile', args=[cls.user.username]
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.id]
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', args=[cls.post.id]
        )
        cls.POST_EDIT_REDIRECT = (
            f'/auth/login/?next=/posts/{cls.post.id}/edit/'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_create_post(self):
        """Проверка создания поста."""
        initial_posts = set(Post.objects.all())
        form_data = {
            'text': 'Тестовый текст2',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.PROFILE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        final_posts = set(Post.objects.all()) - initial_posts
        self.assertEqual(len(final_posts), 1)
        post = final_posts.pop()
        mapping = {
            post.author: self.user,
            post.text: 'Тестовый текст2',
            post.group.pk: self.group.id,
        }
        for form, value in mapping.items():
            with self.subTest(form=form):
                self.assertEqual(form, value)

    def test_form_create_post_with_image(self):
        """Проверка создания поста с картинкой."""
        initial_posts = set(Post.objects.all())
        form_data = {
            'text': 'Тестовый текст2',
            'group': self.group.id,
            'author': self.user,
            'image': uploaded
        }
        response = self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.PROFILE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        final_posts = set(Post.objects.all()) - initial_posts
        self.assertEqual(len(final_posts), 1)
        post = final_posts.pop()
        mapping = {
            post.author: self.user,
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.image: 'posts/small.gif'
        }
        for form, value in mapping.items():
            with self.subTest(form=form):
                self.assertEqual(form, value)

    def test_forms_edit_post(self):
        """Проверка редактирования поста."""
        initial_posts = len(Post.objects.all())
        form_data = {
            'text': 'Измененный тестовый текст',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        final_posts = len(Post.objects.all())
        post = Post.objects.last()
        self.assertRedirects(response, self.POST_DETAIL_URL)
        mapping = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.post.author,
            initial_posts: final_posts,
        }
        for form, value in mapping.items():
            with self.subTest(form=form):
                self.assertEqual(form, value)


class CommentFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.ADD_COMMENT_URL = reverse(
            'posts:add_comment', args=[cls.post.id]
        )

    def test_create_comment(self):
        """Проверка, что авторизованный пользователь
        может создать комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            'post_id': self.post.id,
            'text': 'Тестовый комментарий.'
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Comment.objects.count(), comments_count + 1
        )
        comment = Comment.objects.last()
        mapping = {
            comment.author: self.user,
            comment.text: form_data['text'],
            comment.post.id: form_data['post_id']
        }
        for form, value in mapping.items():
            with self.subTest(form=form):
                self.assertEqual(form, value)

    def test_anonymous_cant_create_comment(self):
        """Проверка, что не авторизованный пользователь
        не может создать комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            'post_id': self.post.id,
            'text': 'Тестовый комментарий.'
        }
        response = self.guest_client.post(
            self.ADD_COMMENT_URL,
            data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count)
