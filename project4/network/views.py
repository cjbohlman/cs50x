from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse




from .models import User, Post

class NewPostForm(forms.Form):
    post = forms.CharField(min_length=1, widget=forms.Textarea)


def index(request):
    return render(request, "network/index.html", {
        "new_post": NewPostForm()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def new(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post_text = form.cleaned_data["post"]
            post = Post(post_text = post_text,
                        author = request.user,
                        likecount=0)
            post.save()
            
        return HttpResponseRedirect(reverse("index"))
    else:
        raise Http404("Wrong request type.")

@login_required
def posts(request, post_type):
    if post_type == "all":
        posts = Post.objects.all()
    elif post_type == "following":
        # Filter on followed users
        posts = Post.objects.filter(
            user=""
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return posts in reverse chronologial order
    posts = posts.order_by("-timestamp").all()
    return JsonResponse([post.serialize() for post in posts], safe=False)