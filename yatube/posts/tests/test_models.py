from django.test import TestCase

from ..models import Group, Post, User, Comment


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
            post=cls.post,
            author=cls.user,
            text='Комментарий ' * 10,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:Post.TEXTMAX], str(self.post))
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(self.comment.text[:Comment.COMMENTMAX],
                         str(self.comment))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'Post': {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа'
            },
            'Comment': {
                'text': 'Текст комментария',
                'author': 'Автор',
                'created': 'Дата публикации',
            }
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                if field == self.post:
                    self.assertEqual(
                        field._meta.get_field(field).verbose_name,
                        expected_value
                    )
                if field == self.comment:
                    self.assertEqual(
                        self.comment._meta.get_field(field).verbose_name,
                        expected_value
                    )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'Post': {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
            },
            'Comment': {
                'text': 'Введите текст комментария',
            }
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                if field == self.post:
                    self.assertEqual(
                        self.post._meta.get_field(field).help_text,
                        expected_value)
                if field == self.comment:
                    self.assertEqual(
                        self.comment._meta.get_field(field).help_text,
                        expected_value)
