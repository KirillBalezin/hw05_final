from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

INDEX = ' / '
INDEX_URL = 'posts:index'
POST_CREATE = 'create/'
POST_CREATE_URL = 'posts:post_create'
FOLLOW = 'follow/'
FOLLOW_URL = 'posts:follow_index'


class TaskURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание группы',
            slug='test_slug'
        )
        cls.user = User.objects.create_user(
            username='HasNoName'
        )
        cls.post = Post.objects.create(
            text='Текст для тестов',
            group=cls.group,
            author=cls.user
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.GROUP_LIST = f'/group/{cls.group.slug}/'
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list',
            args=[cls.group.slug])
        cls.PROFILE = f'/profile/{cls.user.username}/'
        cls.PROFILE_URL = reverse(
            'posts:profile',
            args=[cls.user.username])
        cls.POST_DETAIL = f'/posts/{cls.post.id}/'
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id])
        cls.POST_EDIT = f'/posts/{cls.post.id}/edit/'
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id])
        cls.POST_COMMENT = f'/posts/{cls.post.id}/comment/'
        cls.POST_COMMENT_URL = reverse(
            'posts:add_comment',
            args=[cls.post.id])
        cls.POST_FOLLOW = f'/profile/{cls.user.username}/follow/'
        cls.POST_FOLLOW_URL = reverse(
            'posts:profile_follow',
            args=[cls.user.username])
        cls.POST_UNFOLLOW = f'/profile/{cls.user.username}/unfollow/'
        cls.POST_UNFOLLOW_URL = reverse(
            'posts:profile_unfollow',
            args=[cls.user.username])

    def test_routes(self):
        urls = {
            INDEX: INDEX_URL,
            POST_CREATE: POST_CREATE_URL,
            self.GROUP_LIST: self.GROUP_LIST_URL,
            self.PROFILE: self.PROFILE_URL,
            self.POST_DETAIL: self.POST_DETAIL_URL,
            self.POST_EDIT: self.POST_EDIT_URL,
            self.POST_COMMENT: self.POST_COMMENT_URL,
            FOLLOW: FOLLOW_URL,
            self.POST_FOLLOW: self.POST_FOLLOW_URL,
            self.POST_UNFOLLOW: self.POST_UNFOLLOW_URL
        }
        for address, route_name in urls.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.authorized_client.get(address).status_code,
                    self.authorized_client.get(route_name).status_code
                )
