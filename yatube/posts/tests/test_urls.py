from django.test import TestCase, Client
from posts.models import User, Group, Post

class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.user = User.objects.create(username='test_user')

        cls.group = Group.objects.create(
            title='текстовый заголовок',
            slug='test-slug',
            description='тестовое описание'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )
    
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = StaticURLTests.user
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)


# Проверяем общедоступные страницы
    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')  
        self.assertEqual(response.status_code, 200)
    
    def test_group_slug(self):
        """Страница /group/slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)
    
    def test_profile_username(self):
        """Страница /profile/username/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/test_user/')
        self.assertEqual(response.status_code, 200)
        
    def test_post_id(self):
        """Страница /posts/post_id/ доступна любому пользователю."""
        post_id = self.post.pk
        response = self.guest_client.get(f'/posts/{ post_id }/')
        self.assertEqual(response.status_code, 200)  
     
 
# только для автора
    def test_posts_post_id_edit(self):
        """Страница posts/post_id_edit/ доступна только автору"""
        self.assertEqual(self.post.author.username, self.user.username)
    
    
# Проверяем доступность страниц для авторизованного пользователя
    def test_create(self):
        """страница /create/ доступна только авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

# 404
    def test_unexisting_page(self):
        """Несуществующая страница"""
        response = self.authorized_client.get('/posts/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        
# Проверяем редиректы для неавторизованного пользователя
    def test_task_list_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')
        
#проверяем шаблоны по адресам
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        post_id = str(self.post.pk)
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test_user/': 'posts/profile.html',
            '/posts/' + post_id + '/': 'posts/post_detail.html',
            '/posts/' + post_id + '/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
