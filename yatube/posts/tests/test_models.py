from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='тест заголовок',
            slug='test_slug',
            description='тест описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='тест текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post

        field_object_name = {
            post: self.post.text,
        }
        for value, expected in field_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(post), expected[:15]
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='тест заголовок',
            slug='test_slug',
            description='тест описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='тест текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = GroupModelTest.group

        field_object_name = {
            group: self.group.title,
        }
        for value, expected in field_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(group), expected
                )
