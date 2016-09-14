from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from urllib.parse import quote_plus

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from comments.forms import CommentForm
from comments.models import Comment
from posts import models, forms, utils


def posts_update(request, slug):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    post = get_object_or_404(models.Post, slug=slug)
    form = forms.PostForm(instance=post)
    if request.method == "POST":
        form = forms.PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, "Edited Post")
            return HttpResponseRedirect(post.get_absolute_url())
    context = {"post": post, "title": "nuzz", "form": form}
    return render(request, "post_form.html", context)



def posts_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = forms.PostForm()
    if request.method == "POST":
        form = forms.PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "New Post Created")
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            messages.error(request, "ERROR! ERROR! eRROR!")
    context = {"form": form}
    return render(request, "post_form.html", context)


def posts_list(request):
    today = timezone.now().date()
    posts_list = models.Post.objects.active()     #.filter(draft=False).filter(publish__lte=timezone.now()) .order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        posts_list = models.Post.objects.all()
    search = request.GET.get("q")
    if search:
        posts_list = models.Post.objects.filter(
            Q(title__icontains=search) |
            Q(context__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        ).distinct()
    paginator = Paginator(posts_list, 5) # Show 5 contacts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    context = {"posts": posts, "title": "list", "today": today}
    return render(request, "post_list.html", context)





def posts_detail(request, slug):
    post = get_object_or_404(models.Post, slug=slug)
    if not request.user.is_staff or not request.user.is_superuser:
        if post.draft or post.publish > timezone.now().date():
            raise Http404
    share_string = quote_plus(post.context)
    # print(utils.get_read_time(post.content))
    print(utils.get_read_time(post.get_markdown()))
    initial_data = {
        'content_type': post.get_content_type,
        'object_id': post.id,
    }

    # content_type = ContentType.objects.get_for_model(post)
    # obj_id = post.id
    # doing this --- Post.objects.get(id=post.id)
    # comments = Comment.objects.filter(content_type=content_type, object_id=obj_id)

    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get('content_type')
        # content_type = ContentType.objects.get(model=c_type)
        content_type = ContentType.objects.get_for_model(post)
        obj_id = form.cleaned_data.get('object_id')
        content_data = form.cleaned_data.get('content')

        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except TypeError:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()   # parent_qs[0]

        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            parent=parent_obj,
            content=content_data,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = post.comments    # Comment.objects.filter_by_instance(post)

    context = {
        "post": post,
        "title": "details",
        'share_string': share_string,
        'comments': comments,
        'comment_form': form
    }

    return render(request, "post_detail.html", context)


def posts_delete(request, slug):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    post = get_object_or_404(models.Post, slug=slug)
    post.delete()
    messages.success(request, "Post Deleted!")
    return redirect("posts:list")
