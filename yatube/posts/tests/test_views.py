from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='anton')
        cls.group = Group.objects.create(
            title='label',
            slug='test-slug',
            description='labels description for testing urls'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            pub_date='28.06.2021',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def check_post_context(self, context):
        if context.get('post'):
            post = context['post']
        else:
            post = context['page'][0]
        self.assertEqual(post.text, PostViewsTests.post.text)
        self.assertEqual(post.author, PostViewsTests.post.author)
        self.assertEqual(post.group, PostViewsTests.post.group)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            reverse('index'): 'index.html',
            reverse(
                'group',
                kwargs={'slug': PostViewsTests.group.slug}): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse('post_edit',
                    kwargs={'username': PostViewsTests.author,
                            'post_id': PostViewsTests.post.id}):
            'new_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        self.check_post_context(response.context)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostViewsTests.group.slug}))
        self.assertEqual(
            response.context['group'].title, PostViewsTests.group.title)
        self.assertEqual(
            response.context['group'].slug, PostViewsTests.group.slug)
        self.assertEqual(response.context['group'].description,
                         PostViewsTests.group.description)

    def test_new_edit_post_page_shows_correct_context(self):
        response = self.authorized_client.post(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': PostViewsTests.author.username}))
        self.check_post_context(response.context)

    def test_post_with_group_on_home_page(self):
        response = self.authorized_client.get(reverse('index'))
        self.check_post_context(response.context)

    def test_post_with_group_on_group_page(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostViewsTests.group.slug}))
        self.check_post_context(response.context)

    def test_post_id_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={'username': PostViewsTests.author.username,
                        'post_id': PostViewsTests.post.id}))
        self.check_post_context(response.context)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='label',
            slug='test-slug',
            description='labels description for testing paginator'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'{i} тестовый текст',
                author=cls.user,
                group=cls.group,
            )
        cls.client = Client()

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

    def test_paginator_profile_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'profile',
            kwargs={'username': f'{PaginatorViewTest.user.username}'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_profile_page_contains_three_records(self):
        response = self.client.get(reverse(
            'profile',
            kwargs={
                'username': f'{PaginatorViewTest.user.username}'
            }) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
