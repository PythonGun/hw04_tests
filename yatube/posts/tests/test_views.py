from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.auth = User.objects.create_user(username="auth")

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.another_group = Group.objects.create(
            title="Другая тестовая группа",
            slug="another-test-slug",
            description="Тестовое описание",
        )

        cls.post = Post.objects.create(
            author=cls.auth,
            group=cls.group,
            text='тест текст',
        )

    def setUp(self):
        self.authorized_client_auth = Client()
        self.authorized_client_auth.force_login(PostPagesTests.auth)

    def test_create_post(self):
        """Тестовый пост не попал в группу, для которой не был предназначен"""
        self.assertFalse(
            PostPagesTests.another_group.posts.filter(
                id=PostPagesTests.post.id
            )
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:post_create"): "posts/post_create.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile",
                kwargs={"username": f"{PostPagesTests.auth.username}"},
            ): "posts/profile.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{PostPagesTests.post.id}"},
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostPagesTests.post.id}"},
            ): "posts/post_create.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def page_show_correct_context(self, post):
        """Шаблон page_obj сформирован с правильным контекстом."""

        urls = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test-slug"}),
            reverse(
                "posts:profile",
                kwargs={"username": f"{PostPagesTests.auth.username}"},
            ),
        ]
        for reverse_name in urls:
            response = self.authorized_client_auth.get(reverse_name)
            first_object = response.context["page_obj"][0]
            first_obj_field_value = {
                first_object.text: PostPagesTests.post.text,
                first_object.group: PostPagesTests.group,
                first_object.author: PostPagesTests.auth,
            }
            for field, value in first_obj_field_value.items():
                with self.subTest(field=field):
                    self.assertEqual(field, value)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{PostPagesTests.post.id}"},
            )
        )
        context_value = {
            response.context.get("post").text: PostPagesTests.post.text,
            response.context.get("post").group: PostPagesTests.group,
            response.context.get("post").image: PostPagesTests.post.image,
            response.context.get("post").author: PostPagesTests.auth,
            response.context.get("comments").latest(
                "pk"
            ): PostPagesTests.comment,
            response.context.get(
                "posts_count"
            ): PostPagesTests.auth.posts.count(),
        }
        for context, value in context_value.items():
            with self.subTest(context=context):
                self.assertEqual(context, value)

    def test_post_list_pages_show_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": f"{PostPagesTests.group.slug}"},
            )
        )
        self.assertEqual(
            response.context.get("group").title, PostPagesTests.group.title
        )
        self.assertEqual(
            response.context.get("group").description,
            PostPagesTests.group.description,
        )

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse(
                "posts:profile",
                kwargs={"username": f"{PostPagesTests.auth.username}"},
            )
        )
        self.assertEqual(response.context.get("author"), PostPagesTests.auth)
        self.assertEqual(
            response.context.get("posts_count"),
            PostPagesTests.auth.posts.count(),
        )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse("posts:post_create")
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.auth = User.objects.create_user(username="auth")

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for cls.post in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.auth,
                text='Тестовый текст',
                group=cls.group,
            )

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        for reverse_name in PaginatorViewTest.urls:
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        for reverse_name in PaginatorViewTest.urls:
            response = self.client.get(reverse_name + "?page=2")
            self.assertEqual(len(response.context["page_obj"]), 3)
