from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


AUTHOR_USERNAME = "Testname"
POST_TEXT = "Тестовый текст"
GROUP_TITLE = "Тестовая группа"
SLUG = "SlugTest"
GROUP_DESCRIPTION = "Тестовое описание"
SECOND_GROUP_TITLE = "Вторая тестовая группа"
SECOND_SLUG = "new_group"
SECOND_GROUP_DESCRIPTION = "Тестовое описание второй группы"
PROFILE_URL = reverse("posts:profile", args=[AUTHOR_USERNAME])
POST_CREATE_URL = reverse("posts:post_create")


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.second_group = Group.objects.create(
            title=SECOND_GROUP_TITLE,
            slug=SECOND_SLUG,
            description=SECOND_GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text=POST_TEXT,
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])

    def setUp(self):
        self.guest = Client()
        self.author_client = Client()
        self.author_client.force_login(self.auth_user)

    def test_post_edit(self):
        """Валидная форма обновляет выбранный пост."""
        post_count = Post.objects.count()
        form_data = {
            "text": "Новый текст для поста",
            "group": self.second_group.id
        }
        self.author_client.post(
            self.POST_EDIT_URL, data=form_data, follow=True)
        refresh_post = self.author_client.get(
            self.POST_DETAIL_URL).context["post"]
        self.assertEqual(refresh_post.text, form_data["text"])
        self.assertEqual(refresh_post.group.id, form_data["group"])
        self.assertEqual(refresh_post.author, self.post.author)
        self.assertEqual(post_count, Post.objects.count())

    def test_create_post_form(self):
        """Валидная форма создает новый пост."""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст 123",
            "group": self.group.id,
        }
        response = self.author_client.post(POST_CREATE_URL, data=form_data)
        post = Post.objects.latest("id")
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.auth_user)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(Post.objects.count() - post_count, 1)

    def test_edit_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_fields = {
            'text': 'Тестовый текст изм',
            'group': PostFormTest.group.pk,
        }
        response = self.author_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostFormTest.post.id}),
            data=form_fields,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostFormTest.post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTest.group.pk,
                text=form_fields['text'],
                id=PostFormTest.post.id,
            )
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.text, form_fields['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group_id, form_fields['group'])
