import tempfile
import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

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

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username=AUTHOR_USERNAME)
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
            image=None,
        )
        cls.POST_DETAIL_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])

    def setUp(self):
        self.post_count = Post.objects.count()
        self.guest = Client()
        self.author_client = Client()
        self.author_client.force_login(self.auth_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {'text': 'Тестовый текст',
                     'group': self.group.id,
                     'image': self.uploaded,
                     }
        response = self.author_client.post(POST_CREATE_URL, data=form_data,
                                           follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.auth_user}))
        post = Post.objects.last()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.auth_user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_edit(self):
        uploaded_edit = SimpleUploadedFile(
            name='small1.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        """Валидная форма обновляет выбранный пост."""
        form_data = {
            "text": "Новый текст для поста",
            "group": self.second_group.id,
            'image': uploaded_edit
        }
        self.author_client.post(
            self.POST_EDIT_URL, data=form_data, follow=True)
        refresh_post = self.author_client.get(
            self.POST_DETAIL_URL).context["post"]
        self.assertEqual(refresh_post.text, form_data["text"])
        self.assertEqual(refresh_post.group.id, form_data["group"])
        self.assertEqual(refresh_post.author, self.post.author)
        self.assertEqual(self.post_count, Post.objects.count())
        self.assertEqual(refresh_post.image, 'posts/small1.gif')
