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

        cls.user = User.objects.create_user(username='test_user')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст поста',
        )

        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test_user'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create.html',
            reverse('posts:post_create'): 'posts/create.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        for post in Post.objects.all():
            response = self.authorized_client.get(reverse('posts:index'))
            first_object = response.context['page_obj']
            self.assertIn(post, first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        for post in Post.objects.all():
            response = self.authorized_client.get(
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            )
            first_object = response.context['page_obj']
            self.assertIn(post, first_object)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        for post in Post.objects.all():
            response = self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': 'test_user'})
            )
            first_object = response.context['page_obj']
            self.assertIn(post, first_object)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        first_object = response.context['post_detail']
        self.assertEqual(first_object, PostPagesTests.post)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        username_context = response.context['username']
        self.assertEqual(username_context, PostPagesTests.user)
        is_edit_context = response.context.get('is_edit')
        self.assertTrue(is_edit_context)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        username_context = response.context['username']
        self.assertEqual(username_context, PostPagesTests.user)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for cls.post in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_first_page_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_page_contains_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_paginator_group_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'group', kwargs={'slug': f'{PaginatorViewTest.group.slug}'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_group_page_contains_three_records(self):
        response = self.client.get(reverse(
            'group',
            kwargs={'slug': f'{PaginatorViewTest.group.slug}'}) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_index_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'profile',
            kwargs={'username': f'{PaginatorViewTest.user.username}'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse(
            'profile',
            kwargs={
                'username': f'{PaginatorViewTest.user.username}'
            }) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
