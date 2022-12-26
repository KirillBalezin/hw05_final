from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from ..models import Group, Post, User

INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:post_create')


class PostURLTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list', kwargs={'slug': f'{cls.group.slug}'}
        )
        cls.PROFILE_URL = reverse(
            'posts:profile', kwargs={'username': f'{cls.user.username}'})
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.POST_CREATE_REDIRECT = '/auth/login/?next=/create/'
        cls.POST_EDIT_REDIRECT = (
            f'/auth/login/?next=/posts/{cls.post.id}/edit/')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            CREATE_POST_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_for_anonymus(self):
        """Страницы доступны любым пользователям."""
        url = (
            INDEX_URL,
            self.GROUP_LIST_URL,
            self.PROFILE_URL,
            self.POST_DETAIL_URL,
        )
        for adress in url:
            response = self.guest_client.get(adress)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(CREATE_POST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_redirect_anonymous_on_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        pages = {
            CREATE_POST_URL: self.POST_CREATE_REDIRECT,
            self.POST_EDIT_URL: self.POST_EDIT_REDIRECT
        }
        for page, value in pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertRedirects(response, value)

    def test_post_edit_for_author(self):
        """Старница /posts/<post_id>/edit/ доступна автору поста"""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
