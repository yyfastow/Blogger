from django import forms

from pagedown.widgets import PagedownWidget

from posts import models


class PostForm(forms.ModelForm):
    context = forms.CharField(widget=PagedownWidget(show_preview=False)) # set show_preview to True or just remove it to have the shom show how the form will look like on page
    publish = forms.DateField(widget=forms.SelectDateWidget)
    class Meta:
        model = models.Post
        fields = [
            "title",
            "context",
            "image",
            "draft",
            'publish'
        ]