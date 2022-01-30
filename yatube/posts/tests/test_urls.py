from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_techpage(self):
        response = self.guest_client.get('about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_about_authorpage(self):
        response = self.guest_client.get('about/author/')
        self.assertEqual(response.status_code, 200)


class PostURLTest(TestCase):
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
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая группа',
            group=cls.group
        )

    def test_non_existent_page_correct(self):
        response = self.guest_client.get('/non_existent_page/')
        self.assertEqual(response.status_code, 404)

    def test_non_auth_urls_correct(self):
        url_names_non_auth = ['/',
                              '/group/test_slug/',
                              '/profile/HasNoName/',
                              '/posts/1/']
        for address in url_names_non_auth:
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_auth_post_edit_url_correct(self):
        url = '/posts/1/edit/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_auth_user_create_url_correct(self):
        url = '/create/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        url_templates_names_all = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in url_templates_names_all.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
