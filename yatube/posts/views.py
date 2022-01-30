from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .models import Post, Group, User
from .forms import PostForm

from yatube.settings import PAGE_NUM


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    posts = Post.objects.all()

    context = {
        'title': 'Главная страница Ятаб',
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    description = group.description
    title = str(group)

    paginator = Paginator(posts, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': title,
        'group': group,
        'posts': posts,
        'description': description,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):

    template = 'posts/profile.html'
    username = get_object_or_404(User, username=username)
    posts = username.posts.all()
    title = 'Профиль пользователя ' + str(username.get_full_name())

    paginator = Paginator(posts, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts_num = posts.count()

    context = {

        'title': title,
        'username': username,
        'posts_num': posts_num,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_num = post.author.posts.all().count()
    title = str(post)
    template = 'posts/post_detail.html'

    context = {
        'title': title,
        'post': post,
        'post_num': posts_num,
    }
    return render(request, template, context)


@login_required
@csrf_exempt
def post_create(request):

    form = PostForm(request.POST or None)
    groups = Group.objects.all()
    template = 'posts/create_post.html'

    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    groups = Group.objects.all()
    if form.is_valid():
        form = form.save(False)
        form.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
        'groups': groups,
    }
    form = PostForm({'text': post.text, 'group': post.group})
    return render(request, 'posts/create_post.html', context)
