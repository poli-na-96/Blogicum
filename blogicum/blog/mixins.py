from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Comment
from .forms import PostForm, CommentForm


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostMakeChangesMixin:
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if self.posts.author != request.user:
            return redirect('blog:post_detail', self.kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
            author=request.user.id
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )
