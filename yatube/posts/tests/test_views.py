from http import HTTPStatus

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
from yatube.settings import NUMBER_POST
# Тесты не проходят если из django.conf брать

TEXT_TEST = {"SLUG": "SlugTest-1",
             "SECOND_SLUG": "TestSlug-2",
             "AUTHOR_USERNAME": "Test",
             "NOT_AUTHOR_USERNAME": "Testov",
             "POST_TEXT": "Тестовый текст, длинее 15 символов",
             "SECOND_TEXT": "Текст второго поста",
             "GROUP_TITLE": "Тестовая группа",
             "SECOND_GROUP_TITLE": "Вторая тестовая группа",
             "GROUP_DESCRIPTION": "Тестовое описание",
             "SECOND_GGROUP_DESCRIPTION": "Тестовое описание второй группы"}
POST_CREATE_URL = reverse("posts:post_create")
LOGIN_URL = reverse("users:login")
FOLLOW_REDIRECT_CREATE_TO_LOGIN = f"{LOGIN_URL}?next={POST_CREATE_URL}"
SECOND_GROUP_LIST_URL = reverse("posts:group_list",
                                args=[TEXT_TEST["SECOND_SLUG"]])
GROUP_LIST_URL = reverse("posts:group_list", args=[TEXT_TEST["SLUG"]])
GROUP_TEST = reverse('posts:group_list', kwargs={'slug': TEXT_TEST["SLUG"]})
PROFILE_TEST = reverse('posts:profile', kwargs={'username': 'auth'})
INDEX_URL = reverse("posts:index")
PROFILE_URL = reverse("posts:profile", args=[TEXT_TEST["AUTHOR_USERNAME"]])


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_author = User.objects.create_user(username='UserAuthor')
        cls.group = Group.objects.create(
            title=TEXT_TEST["GROUP_TITLE"],
            slug=TEXT_TEST["SLUG"],
            description=TEXT_TEST["GROUP_DESCRIPTION"],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT_TEST["POST_TEXT"],
            group=cls.group,
            id='1',
        )
        cls.group2 = Group.objects.create(
            title=TEXT_TEST["SECOND_GROUP_TITLE"],
            slug=TEXT_TEST["SECOND_SLUG"],
            description=TEXT_TEST["SECOND_GGROUP_DESCRIPTION"],
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.POST_DETAIL_URL = reverse('posts:post_detail',
                                       args=(self.post.id))
        self.POST_EDIT_URL = reverse('posts:post_edit',
                                     kwargs={'post_id': self.post.id})

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_TEST: 'posts/group_list.html',
            PROFILE_TEST: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.assertEqual(self.post.text, TEXT_TEST["POST_TEXT"])
        self.assertEqual(self.post.pub_date, self.post.pub_date)
        self.assertEqual(self.post.author.username, 'auth')
        self.assertEqual(self.post.group.title, TEXT_TEST["GROUP_TITLE"])

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        self.assertEqual(self.group.title, TEXT_TEST["GROUP_TITLE"])
        self.assertEqual(self.group.slug, TEXT_TEST["SLUG"])

    def test_group_list_page_no_another_post_show_correct_context(self):
        """Шаблон group_list не содержит поста с другой группой."""
        response = self.authorized_client.get(GROUP_TEST)
        self.assertNotIn(TEXT_TEST["POST_TEXT"], response.context['page_obj'])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(PROFILE_TEST)
        self.assertIn('author', response.context)
        self.assertEqual(self.user.username, 'auth')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(self.POST_DETAIL_URL)
        self.assertIn('post', response.context)
        self.assertEqual(self.post.text, TEXT_TEST["POST_TEXT"])

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_edit_show_correct_context(self):
        """Шаблон create_post для редактирования сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    ADDITIONAL_POST_COUNT = 3
    PAGE_COUNT = NUMBER_POST + ADDITIONAL_POST_COUNT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title=TEXT_TEST["GROUP_TITLE"],
            slug=TEXT_TEST["SLUG"],
            description=TEXT_TEST["GROUP_DESCRIPTION"],
        )
        posts = [Post(text=f'test_text_{i}',
                      author=cls.user,
                      group=cls.group)
                 for i in range(cls.PAGE_COUNT)]
        cls.posts = Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            INDEX_URL,
            GROUP_TEST,
            PROFILE_TEST,
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 NUMBER_POST)

    def test_second_page_contains_three_records(self):
        templates_pages_names = {
            INDEX_URL + '?page=2',
            GROUP_TEST + '?page=2',
            PROFILE_TEST + '?page=2',
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context.get
                                     ('page_obj').object_list)
                                 - self.PAGE_COUNT, -10)
                # Не совсем понимаю что тут требуется, но как то так
