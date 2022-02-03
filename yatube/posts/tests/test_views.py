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

        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.author_2 = User.objects.create_user(username='author_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        cls.author_post = Post.objects.create(
            text='Текст поста автора',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group_slug = PostPagesTests.group.slug
        user_username = PostPagesTests.user.username
        post_id = PostPagesTests.post.id
        templates_names = {
            'posts/index.html': (reverse('posts:index'),),
            'posts/group_list.html': (
                reverse('posts:group_posts', kwargs={'slug': group_slug}),
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': user_username}),
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': post_id}),
            ),
            'posts/create_post.html': (
                reverse('posts:post_create'),
                reverse('posts:post_edit', kwargs={'post_id': post_id}),
            ),
        }
        for template, reverse_names in templates_names.items():
            for reverse_name in reverse_names:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)
    
    def _post_for_tests(self, context, some_posts):
        self.assertEqual(context.text, some_posts.text)
        self.assertEqual(context.group, some_posts.group)
        self.assertEqual(context.author, some_posts.author)
        self.assertEqual(context.image, PostPagesTests.uploaded)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        all_posts = Post.objects.all()[0]
        self._post_for_tests(first_object, all_posts)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = PostPagesTests.group
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_of_group = group.posts.all()[0]
        self._post_for_tests(first_object, post_of_group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        author = PostPagesTests.user
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        first_object = response.context['page_obj'][0]
        post_of_author = author.posts.all()[0]
        self._post_for_tests(first_object, post_of_author)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id})
        )

        self.assertEqual(response.context['post'], self.post)

        post_title = self.post.text[:30]
        self.assertEqual(response.context['post'].text, post_title)

        post_count = Post.objects.filter(author=self.post.author).count()
        self.assertEqual(
            response.context['post'].author.posts.count(), post_count
        )

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.id})
        )

        form_fields = {
            'text': (forms.fields.CharField, post.text),
            'group': (forms.fields.ChoiceField, post.group.id),
            'image': (forms.fields.ImageField, post.image)

        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def test_create_new_post(self):
        """Тест создания нового поста"""
        new_post = Post.objects.create(
            text='Новый пост',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )
        index_count = Post.objects.count()
        group_count = Post.objects.filter(group=new_post.group).count()
        usercount = Post.objects.filter(author=new_post.author).count()
        template_name = {
            reverse('posts:index'): index_count,
            reverse('posts:group_posts',
                    kwargs={'slug': new_post.group.slug}): group_count,
            reverse('posts:profile',
                    kwargs={'username': new_post.author.username}): usercount,
        }
        for reverse_name, count in template_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), count)


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
