from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def index(request):
    latest = Post.objects.get_queryset().order_by('id')
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.get_queryset().order_by('id').filter(group=group)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html', {"group": group, "page": page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'posts/new.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.get_queryset().order_by('id')
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'author': author, 'author_posts': author_posts, 'paginator': paginator}
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    author=get_object_or_404(User, username=username)
    needed_post=get_object_or_404(Post, id=post_id, author__username=username)
    context = {'author': author, 'post': needed_post}
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if request.user != author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'posts/new.html', {'post': post, 'form': form})
