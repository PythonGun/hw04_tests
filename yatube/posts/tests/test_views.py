from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post
from django.urls import reverse
from django import forms
from mixer.backend.django import mixer
import random
import math

from yatube.settings import PAGE_NUM


User = get_user_model()

class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        
        cls.groups = []
        for i in range(2):
            group = Group.objects.create(
            title=(f'Тестовая группа{i}'),
            slug=(f'test-slug{i}'),
            description=(f'тестовое описание{i}'),
            )
            cls.groups.append(group)
            
        cls.posts = []
        for i in range(13):
            post = Post.objects.create(
            author=cls.user,
            text= (f'Тестовый текст{i}'),
            group=(Group.objects.get(slug='test-slug0'))
            )
            cls.posts.append(post)


    def setUp(self):
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='Dagik')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = str(random.choice(self.posts).pk)     
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:slug', kwargs={'slug':'test-slug0'}):'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':'test_user'}):'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': post_id}):'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': post_id}):'posts/create_post.html',
            reverse('posts:post_create'):'posts/create_post.html',         
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
    
    
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        post = random.choice(response.context['posts'])
        post_fields = {
            'author': Post.objects.get(pk=post.pk).author,
            'group': Post.objects.get(pk=post.pk).group,
            'text': Post.objects.get(pk=post.pk).text,
        }
        for value, expected in post_fields.items():
            with self.subTest(value=value):
                post_field = getattr(post, value)
                self.assertEqual(post_field, expected)          
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    
    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group_slug = 'test-slug0'
        expected_group = Group.objects.get(slug=group_slug)
        response = self.guest_client.get(reverse('posts:slug', args=[group_slug]))
        posts = response.context['posts']
        for post in posts:
            self.assertEqual(post.group, expected_group)
        # self.test_paginator(url_name='posts:slug', slug=group_slug)      
        response = self.client.get(reverse('posts:slug', args=[group_slug]))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:slug', args=[group_slug]) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile', args=['test_user']))
        username = response.context['username']
        page_obj = response.context['page_obj']
        post = random.choice(page_obj)
        self.assertEqual(post.author, username)
        response = self.client.get(reverse('posts:profile', args=['test_user']))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:profile', args=['test_user']) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_id = random.choice(self.posts).pk
        response = self.guest_client.get(reverse('posts:post_detail', args=[post_id]))
        post = response.context['post']
        self.assertEqual(post.pk, post_id)


    def test_create_post_edit_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        post_id = random.choice(self.posts).pk
        response = self.authorized_client.get(reverse('posts:post_edit', args=[post_id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


    def test_additional_create(self):
        """Дополнительная проверка при создании поста на главной странице пройдена."""
        response = self.guest_client.get(reverse('posts:index'))
        posts = response.context['posts']
        post = random.choice(self.posts)
        self.assertIn(post, posts)

    def test_additional_group(self):
        """Дополнительная проверка при создании поста на странице группы пройдена."""
        response = self.guest_client.get(reverse('posts:slug', args=['test-slug0']))
        posts = response.context['posts']
        post = random.choice(self.posts)
        self.assertIn(post, posts)
           
    def test_additional_profile(self):
        """Дополнительная проверка при создании поста на главной странице пройдена."""
        response = self.guest_client.get(reverse('posts:profile', args=['test_user']))
        page_obj = response.context['page_obj']
        post = random.choice(self.posts)
        # print(post)
        # print(page_obj.object_list)
        self.assertIn(post, page_obj.object_list)

    def test_no_additional_group(self):
        """Дополнительная проверка что пост не попал в группу для которой был предназначен"""
        response = self.guest_client.get(reverse('posts:slug', args=['test-slug1']))
        posts = response.context['posts']
        post = random.choice(self.posts)
        self.assertNotIn(post, posts)
        
        
        
        
        
        
        
        
        
        
        
        

    # def test_paginator(self, url_name, slug):
    #     """Паджинатор сформирован правильно."""
    #     response = self.client.get(reverse(url_name, args=[slug]))
    #     self.assertEqual(len(response.context['page_obj']), PAGE_NUM)
    #     posts_num = len(self.posts)
    #     last_page_num = math.ceil(posts_num/PAGE_NUM)
    #     last_posts_num = posts_num - math.floor(posts_num/PAGE_NUM) * PAGE_NUM
    #     response = self.client.get(reverse(url_name, args=[slug]) + '?page=' + str(last_page_num))
    #     self.assertEqual(len(response.context['page_obj']), last_posts_num)