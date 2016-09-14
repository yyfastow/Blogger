from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from comments import models
from comments import forms


# @login_required(login_url='/login/')
@login_required
def comment_delete(request, id):
    comment = get_object_or_404(models.Comment, id=id)
    if comment.user != request.user:
        response = HttpResponse("You do not have permission to delete this comment")
        response.status_code = 403
        return response
        # return render(request, "confirm_delete.html", {'a': a} status_code=403)
    if request.method == 'POST':
        parent_object_url = comment.content_object.get_absolute_url()
        comment.delete()
        messages.success(request, "Comment is deleted")
        return HttpResponseRedirect(parent_object_url)
    return render(request, 'confirm_delete.html', {'comment': comment})


def comment_thread(request, id):
    obj = get_object_or_404(models.Comment, id=id)
    """if not obj.is_parents:
        obj = obj.parent"""

    initial_data = {
        'content_type': obj.content_type,
        'object_id': obj.object_id
    }
    form = forms.CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get('content_type')
        content_type = ContentType.objects.get(model=c_type)
        # content_type = ContentType.objects.get_for_model(post)
        obj_id = form.cleaned_data.get('object_id')
        content_data = form.cleaned_data.get('content')

        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except TypeError:
            parent_id = None
        if parent_id:
            parent_qs = models.Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()   # parent_qs[0]

        new_comment, created = models.Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            parent=parent_obj,
            content=content_data,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    return render(request, 'comment_thread.html', {'comment': obj, 'form': form})
