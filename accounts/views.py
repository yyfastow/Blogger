from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import render, redirect

from accounts import forms


# Create your views here.
def login_view(request):
    next = request.GET.get('next')
    title = "Login"
    form = forms.UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        print(request.user.is_authenticated())
        if next:
            return redirect(next)
        return redirect('/')
    return render(request, "form.html", {"form": form, 'title': title})


def register_view(request):
    next = request.GET.get("next")
    title = "Register"
    form = forms.UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()

        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        print(request.user.is_authenticated())
        if next:
            return redirect(next)
        return redirect('/')
    return render(request, "form.html", {'title': title, 'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')
