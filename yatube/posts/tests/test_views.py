from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group
from django import forms

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_descrioption'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author
        )

        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test_group_slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'test_author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ): 'posts/create_post.html',
        }

    def test_pages_uses_correct_template(self):
        """URL адресс использует соответствующий шаблон"""
        for reverse_name, template in (
            PostViewsTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTests.authorized_author.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)

    def check_post(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.author)

    def test_index_show_correct_context(self):
        """Главная страница сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_client.get(
            reverse('posts:index')
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_group_list_show_correct_context(self):
        """Cтраница группы сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_profile_show_correct_context(self):
        """Страница профиля сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:profile', args=['test_author'])
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_detail_show_correct_context(self):
        """Страница поста сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:post_detail', args=[1])
        )
        post = response.context['post']
        self.check_post(post)

    def test_post_create_show_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:post_edit', args=[1])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_on_pages(self):
        """Проверяем, что новый пост показывается на нужных страницах"""

        self.new_group = Group.objects.create(
            title='new_group',
            slug='new_slug',
            description='something',
        )

        self.new_post = Post.objects.create(
            text='Новый текст',
            group=self.new_group,
            author=self.author,
        )

        form_data = {
            'text': 'Новый текст',
            'group': 'new_group',
        }
        response = self.authorized_author.post(
            reverse('posts:index'),
            data=form_data,
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Новый текст')

        response = self.authorized_author.post(
            reverse('posts:group_list', args=['new_group']),
            data=form_data,
        )
        self.assertEqual(first_post.text, 'Новый текст')

        response = self.authorized_author.post(
            reverse('posts:profile', args=[self.author]),
            data=form_data,
        )
        self.assertEqual(first_post.text, 'Новый текст')

        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='Тестовое описание группы',
        )
        cls.post = [
            Post.objects.create(
                text='Пост №' + str(i),
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group
            )
            for i in range(13)]

    def test_index_page_contains_ten_records(self):

        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)