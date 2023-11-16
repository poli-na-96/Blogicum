import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView, DetailView
)
from django.utils import timezone
from django.urls import reverse_lazy

from .models import Post, Category, User
from .forms import CommentForm, UserForm
from .mixins import PostMixin, PostMakeChangesMixin, CommentMixin


POSTS_ON_PAGE = 10


class IndexListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    queryset = (Post.objects.prefetch_related(
        'comments').select_related('author')
    ).filter(
        pub_date__lte=datetime.datetime.now(tz=timezone.utc),
        is_published=True,
        category__is_published=True
    ).annotate(comment_count=Count('comments'))
    ordering = '-pub_date'
    paginate_by = POSTS_ON_PAGE


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(
    LoginRequiredMixin,
    PostMixin,
    PostMakeChangesMixin,
    UpdateView
):
    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(
    LoginRequiredMixin,
    PostMixin,
    PostMakeChangesMixin,
    DeleteView
):
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        context['comment_count'] = self.object.comments.all().count()
        return context

    def get_object(self):
        post = super().get_object()
        if not post.is_published and post.author != self.request.user:
            raise Http404()
        return post


def profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User.objects.all(), username=username)
    user_posts = profile.posts.all(
    )
    if request.user.username != username:
        user_posts = user_posts.filter(is_published=True)
    user_posts = user_posts.order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count('comments')
    )
    paginator = Paginator(user_posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.all(),
        is_published=True,
        slug=category_slug
    )
    post_list = category.posts.all(
    ).order_by(
        '-pub_date'
    ).filter(
        pub_date__lte=datetime.datetime.now(tz=timezone.utc),
        is_published=True,
        category__slug__exact=category_slug
    ).annotate(
        comment_count=Count('comments')
    )
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'post_list': post_list,
        'page_obj': page_obj
    }
    return render(request, template_name, context)
