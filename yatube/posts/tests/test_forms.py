from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description',
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author,
        )

        cls.form_data_create = {
            'text': 'new_text',
            'group': cls.group.id,
            'username': cls.author.username,
        }

        cls.form_data_edit = {
            'post_id': cls.post.id,
            'text': 'editted_text',
            'group': cls.group.id,
            'author': cls.author,
        }

    def test_create_post(self):
        posts_count = Post.objects.count()

        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=self.form_data_create,
            follow=True,
        )

        self.assertRedirects(
            response, reverse('posts:profile', args=[self.author])
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='new_text',
                author=self.author,
            ).exists()
        )

    def test_edit_post(self):

        response = self.authorized_author.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=self.form_data_edit,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[self.post.id])
        )
        edit_post = Post.objects.latest('id')
        self.assertEqual(edit_post.text, 'editted_text')
        self.assertEqual(edit_post.author, self.author)
        self.assertEqual(edit_post.group, self.group)
