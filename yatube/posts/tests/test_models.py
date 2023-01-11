from django.test import TestCase

from ..models import Group, Post, User, Follow, Comment


FIELD_VERBOSES = {"text": "Текст",
                  "group": "Группа", }
FIELD_HELP_TEXTS = {"text": "Придумайте текст для поста",
                    "group": "Выберите группу"}
FIELD_HELP_TEXTS_FOLLOW = {"user": "Подписчик, который подписывается",
                           "author": 'Автор, на кого подписываются'}
FIELD_VERBOSES_COMMENT = {"author": "Автор комментария",
                          "text": 'Текст комментария'}
FIELD_HELP_TEXTS_COMMENT = {"text": "Введите текст текст комментария"}


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

    def test_help_text_name(self):
        # Тут пока не знаю как сделать
        """help_text полей text и group совпадает с ожидаемым"""
        for value, expected in FIELD_HELP_TEXTS.items():
            with self.subTest(value=value):
                self.assertEqual(Post._meta.get_field(value).help_text,
                                 expected)

    def test_help_text_name_follow(self):
        """help_text полей FOLLOW совпадает с ожидаемым"""
        for value, expected in FIELD_HELP_TEXTS_FOLLOW.items():
            with self.subTest(value=value):
                self.assertEqual(Follow._meta.get_field(value).help_text,
                                 expected)

    def test_help_text_name_comment(self):
        """help_text полей comment совпадает с ожидаемым"""
        for value, expected in FIELD_HELP_TEXTS_COMMENT.items():
            with self.subTest(value=value):
                self.assertEqual(Comment._meta.get_field(value).help_text,
                                 expected)

    def test_verbose_name(self):
        """verbose_name полей text и group совпадает с ожидаемым"""
        for value, expected in FIELD_VERBOSES.items():
            with self.subTest(expected=expected):
                self.assertEqual(Post._meta.get_field(value).verbose_name,
                                 expected)

    def test_verbose_name_follow(self):
        """verbose_name полей  совпадает с ожидаемым"""
        for value, expected in FIELD_VERBOSES_COMMENT .items():
            with self.subTest(expected=expected):
                self.assertEqual(Comment._meta.get_field(value).verbose_name,
                                 expected)
