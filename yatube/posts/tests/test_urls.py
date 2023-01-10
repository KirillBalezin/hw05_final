from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:post_create')
POST_CREATE_REDIRECT = '/auth/login/?next=/create/'
FOLLOW_URL = reverse('posts:follow_index')
NON_EXISTENT_URL = '/unexisting_page/'


class PostURLTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list', args=[cls.group.slug]
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            CREATE_POST_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            FOLLOW_URL: 'posts/follow.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_for_anonymus(self):
        """Страницы доступны пользователям."""
        mapping = {
            self.guest_client: {
                INDEX_URL: HTTPStatus.OK,
                self.GROUP_LIST_URL: HTTPStatus.OK,
                self.PROFILE_URL: HTTPStatus.OK,
                self.POST_DETAIL_URL: HTTPStatus.OK,
                NON_EXISTENT_URL: HTTPStatus.NOT_FOUND
            },
            self.authorized_client: {
                CREATE_POST_URL: HTTPStatus.OK,
                self.POST_EDIT_URL: HTTPStatus.OK,
                FOLLOW_URL: HTTPStatus.OK
            }
        }
        for client, urls in mapping.items():
            for url, status in urls.items():
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_create_redirect_anonymous_on_login(self):
        """Страницы правильно перенаправят пользователей.
        """
        mapping = {
            self.guest_client: {
                CREATE_POST_URL: POST_CREATE_REDIRECT,
                self.POST_EDIT_URL: self.POST_EDIT_REDIRECT
            },
            self.not_author_client: {
                self.POST_EDIT_URL: self.POST_DETAIL_URL
            }
        }
        for client, urls in mapping.items():
            for page, value in urls.items():
                with self.subTest(page=page):
                    response = client.get(page)
                    self.assertRedirects(response, value)
