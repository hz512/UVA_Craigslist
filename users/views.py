from django.contrib import messages
from django.shortcuts import render, redirect
from main import models as main_models
from .forms import UserSignupForm


def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f'Account created for {username}!')
            return redirect("users:login")
        else:
            return render(request, "users/signup.html", {"form": form, "title": "Sign Up"})
    else:
        form = UserSignupForm()
        return render(request, "users/signup.html", {"form": form, "title": "Sign Up"})
