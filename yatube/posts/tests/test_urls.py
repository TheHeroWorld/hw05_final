from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User, Comment


# Передалал все под HTTPstatus
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow_user = User.objects.create(username='FollowUser')
        cls.user_author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментрий',
            post=cls.post,
            author=cls.user,
        )

        cls.INDEX = reverse('posts:index')
        cls.GROUP_LIST = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug}
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.PROFILE = reverse(
            'posts:profile', kwargs={'username': cls.post.author}
        )
        cls.POST_CREATE = reverse('posts:post_create')
        cls.POST_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.UNEXISTING_PAGE = '/unexistint_page/'
        cls.LOGIN = reverse('users:login')
        cls.COMMENT = reverse('posts:add_comment', kwargs={'post_id':
                              PostURLTests.post.id})
        cls.FOLLOW = reverse('posts:profile_follow',
                             kwargs={'username': cls.follow_user})
        cls.UNFOLLOW = reverse('posts:profile_unfollow',
                               kwargs={'username': cls.follow_user})

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.user)

    def test_url_exists_at_guest_client(self):
        """Проверка доступа страниц для всех и вся"""
        guest_client_url_code = (
            (self.guest_client, self.INDEX, HTTPStatus.OK),
            (self.guest_client, self.GROUP_LIST, HTTPStatus.OK),
            (self.guest_client, self.PROFILE, HTTPStatus.OK),
            (self.guest_client, self.POST_DETAIL, HTTPStatus.OK),
            (self.guest_client, self.POST_EDIT, HTTPStatus.FOUND),
            (self.guest_client, self.POST_CREATE, HTTPStatus.FOUND),
            (self.guest_client, self.UNEXISTING_PAGE, HTTPStatus.NOT_FOUND),
            (self.guest_client, self.COMMENT, HTTPStatus.FOUND),
            (self.guest_client, self.FOLLOW, HTTPStatus.FOUND),
            (self.guest_client, self.UNFOLLOW, HTTPStatus.FOUND),
        )
        author_client_url_code = (
            (self.author_client, self.INDEX, HTTPStatus.OK),
            (self.author_client, self.GROUP_LIST, HTTPStatus.OK),
            (self.author_client, self.PROFILE, HTTPStatus.OK),
            (self.author_client, self.POST_DETAIL, HTTPStatus.OK),
            (self.author_client, self.POST_EDIT, HTTPStatus.OK),
            (self.author_client, self.POST_CREATE, HTTPStatus.OK),
            (self.author_client, self.UNEXISTING_PAGE, HTTPStatus.NOT_FOUND),
            (self.author_client, self.COMMENT, HTTPStatus.FOUND),
            (self.author_client, self.FOLLOW, HTTPStatus.FOUND),
            (self.author_client, self.UNFOLLOW, HTTPStatus.FOUND),
        )
        not_author_client_url_code = (
            (self.not_author_client, self.INDEX, HTTPStatus.OK),
            (self.not_author_client, self.GROUP_LIST, HTTPStatus.OK),
            (self.not_author_client, self.PROFILE, HTTPStatus.OK),
            (self.not_author_client, self.POST_DETAIL, HTTPStatus.OK),
            (self.not_author_client, self.POST_EDIT, HTTPStatus.FOUND),
            (self.not_author_client, self.POST_CREATE, HTTPStatus.OK),
            (self.not_author_client, self.UNEXISTING_PAGE,
                HTTPStatus.NOT_FOUND),
            (self.not_author_client, self.COMMENT,
                HTTPStatus.FOUND),
            (self.not_author_client, self.FOLLOW,
                HTTPStatus.FOUND),
            (self.not_author_client, self.UNFOLLOW,
                HTTPStatus.FOUND),
        )

        for client, url, code in author_client_url_code:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

        for client, url, code in guest_client_url_code:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

        for client, url, code in not_author_client_url_code:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_guest_not_edit_post(self):
        """Страница post_edit недоступна неавторизованному
        пользователю и перенаправляет его на страницу авторизации"""
        response = self.guest_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostURLTests.post.id}),
            follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{ PostURLTests.post.id}/edit/')

    def test_not_author_not_edit_post(self):
        """ Не автор не может редактировать пост"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostURLTests.post.id}),
            follow=True)
        self.assertRedirects(
            response, f'/posts/{ PostURLTests.post.id}/')

    def test_guest_not_edit_post(self):
        """Страница post_edit недоступна неавторизованному
        пользователю и перенаправляет его на страницу авторизации"""
        response = self.guest_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostURLTests.post.id}),
            follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{ PostURLTests.post.id}/edit/')
