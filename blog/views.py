from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail

from django.views.generic import ListView, DetailView
from .forms import EmailPostForm, CommentForm
from blog.models import Post, Comment

# Create your views here.


class PostListView(ListView):
    queryset = Post.objects.filter(status="published")
    template_name = "blog/post_list.html"
    paginate_by = 3
    context_object_name = "posts"
    ordering = ("-publish",)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status="published",
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    print(request.POST)
    print(post)
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {"post": post, "comments": comments, "comment_form": comment_form},
    )


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, "abdulkhay.payziev@gmail.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request, "blog/share.html", {"post": post, "form": form, "sent": sent}
    )