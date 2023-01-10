from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginate


def index(request):
    """Главная страниц."""
    return render(
        request, 'posts/index.html',
        {'page_obj': paginate(request, Post.objects.all())}
    )


def group_posts(request, slug):
    """Посты группы."""
    return render(
        request, 'posts/group_list.html', {
            'page_obj': paginate(
                request, get_object_or_404(Group, slug=slug).posts.all()
            ),
            'group': get_object_or_404(Group, slug=slug)
        }
    )


def profile(request, username):
    """Профиль пользователя."""
    author = get_object_or_404(User, username=username)
    return render(
        request, 'posts/profile.html', {
            'page_obj': paginate(request, author.posts.all()),
            'author': author,
            'following': (
                request.user.is_authenticated and Follow.objects.filter(
                    user=request.user, author=author).exists())
        }
    )


def post_detail(request, post_id):
    """Подробности поста."""
    return render(
        request, 'posts/post_detail.html', {
            'post': get_object_or_404(Post, pk=post_id),
            'form': CommentForm(),
            'comments': get_object_or_404(Post, id=post_id).comments.all()
        }
    )


@login_required
def post_create(request):
    """Создание поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None)
    if not form.is_valid():
        if request.user != post.author:
            return redirect('posts:post_detail', post_id=post.id)
        form = PostForm(instance=post)
        is_edit = 'is_edit'
        context = {
            'form': form,
            'post': post,
            'is_edit': is_edit
        }
        return render(request, 'posts/create_post.html', context)
    form = PostForm(request.POST, files=request.FILES or None, instance=post)
    form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Посты авторов, на которых подписан текущий пользователь."""
    return render(
        request, 'posts/follow.html', {
            'page_obj': paginate(
                request, Post.objects.filter(
                    author__following__user=request.user))})


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    get_object_or_404(
        Follow, user=request.user, author__username=username
    ).delete()
    return redirect('posts:profile', username=username)
