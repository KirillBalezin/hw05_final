import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Follow, Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

RANGE_POSTS = 13
PAGINATE_PAGE_SECOND = 3

INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:post_create')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list', kwargs={'slug': f'{cls.group.slug}'}
        )
        cls.PROFILE_URL = reverse(
            'posts:profile', kwargs={'username': f'{cls.user.username}'}
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        group_posts = response.context['page_obj'][0]
        post_context = {
            group_posts.text: 'Тестовый пост',
            group_posts.author: self.user,
            group_posts.group: self.group,
            group_posts.image: 'posts/small.gif'
        }
        for context, value in post_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, value)

    def test_views_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_LIST_URL)
        group_posts = response.context['page_obj'][0]
        group_context = {
            group_posts.text: 'Тестовый пост',
            group_posts.author: self.user,
            group_posts.group: self.group,
            group_posts.image: 'posts/small.gif'
        }
        for context, value in group_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, value)

    def test_views_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.PROFILE_URL)
        group_posts = response.context['page_obj'][0]
        profile_context = {
            group_posts.text: 'Тестовый пост',
            group_posts.author: self.user,
            group_posts.group: self.group,
            group_posts.image: 'posts/small.gif'
        }
        for context, value in profile_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, value)

    def test_views_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        response_context = response.context['post']
        post_context = {
            response_context.text: 'Тестовый пост',
            response_context.author: self.user,
            response_context.group: self.group,
            response_context.image: 'posts/small.gif'
        }
        for context, value in post_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, value)

    def test_views_create_post_and_post_edit_pages_show_correct_context(self):
        """Шаблоны post_create и post_edit
        сформирован с правильным контекстом."""
        post_context = (
            CREATE_POST_URL,
            self.POST_EDIT_URL,
        )
        for context in post_context:
            response = self.authorized_client.get(context)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField}
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_views_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group,
        )
        mapping = (
            self.authorized_client.get(INDEX_URL),
            self.authorized_client.get(self.GROUP_LIST_URL),
            self.authorized_client.get(self.PROFILE_URL),
        )
        for response in mapping:
            object = response.context['page_obj']
            self.assertIn(post, object)

    def test_cache_context(self):
        """Проверка кэширования страницы index"""
        before_create_post = self.authorized_client.get(
            reverse('posts:index'))
        first_item_before = before_create_post.content
        Post.objects.create(
            author=self.user,
            text='Тестотовый текст проверки кэша',
            group=self.group)
        after_create_post = self.authorized_client.get(reverse('posts:index'))
        first_item_after = after_create_post.content
        self.assertEqual(first_item_after, first_item_before)
        cache.clear()
        after_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_item_after, after_clear)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list', kwargs={'slug': f'{cls.group.slug}'}
        )
        cls.PROFILE_URL = reverse(
            'posts:profile', kwargs={'username': f'{cls.user.username}'}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        posts = [
            Post(
                text=f'Тестовый текст {i}', group=self.group, author=self.user,
            ) for i in range(RANGE_POSTS)]
        Post.objects.bulk_create(posts)

    def test_first_and_second_pages_contains_ten_records(self):
        """Проверка: количество постов на первой и второй страницах."""
        pages = (
            INDEX_URL,
            self.PROFILE_URL,
            self.GROUP_LIST_URL,
        )
        for page in pages:
            page_numbers = {
                page: settings.PAGINATE_PAGE,
                ((page) + '?page=2'): PAGINATE_PAGE_SECOND
            }
            for page_number, count_page in page_numbers.items():
                with self.subTest(page_number=page_number):
                    response = self.client.get(page_number)
                    self.assertEqual(
                        len(response.context['page_obj']), count_page
                    )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='someauthor')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.FOLLOW_INDEX_URL = reverse('posts:follow_index')

    def test_follower(self):
        """Возможность подписки на автора."""
        subscribers_before = Follow.objects.count()
        Follow.objects.create(
            user=self.user, author=self.author
        )
        subscribers_after = Follow.objects.count()
        self.assertEqual(subscribers_after, subscribers_before + 1)

    def test_follower_see_new_post(self):
        """У подписчика появляется новый пост автора."""
        new_post_follower = Post.objects.create(
            author=self.author,
            text='Текстовый текст')
        Follow.objects.create(
            user=self.user, author=self.author
        )
        response = self.authorized_client.get(self.FOLLOW_INDEX_URL)
        new_posts = response.context['page_obj']
        self.assertIn(new_post_follower, new_posts)

    def test_unfollower_no_see_new_post(self):
        """У не подписчика не появляется новый пост автора"""
        new_post_follower = Post.objects.create(
            author=self.author,
            text='Текстовый текст')
        response = self.authorized_client.get(self.FOLLOW_INDEX_URL)
        new_post_unfollower = response.context['page_obj']
        self.assertNotIn(new_post_follower, new_post_unfollower)
