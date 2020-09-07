from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.urls import reverse

import markdown2
import random

from . import util

class SearchForm(forms.Form):
    article = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))

class NewArticleForm(forms.Form):
    title = forms.CharField(min_length=1)
    article = forms.CharField(min_length=1, widget=forms.Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def wiki_title(request, title):
    article = util.get_entry(title)
    if article is None:
        # error page
        raise Http404("Page does not exist.")
    else:

        return render(request, "encyclopedia/article.html", {
            "article": markdown2.markdown(article) ,
            "title": title,
            "form": SearchForm()
        })

def random_article(request):
    articles = util.list_entries()
    return HttpResponseRedirect(reverse('article', args=[random.choice(articles)]))

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data["article"]
            if article in util.list_entries():
                return HttpResponseRedirect(reverse('article', args=[article]))
            else:
                return render(request, "encyclopedia/index.html", {
                    "entries": [s for s in util.list_entries() if article.lower() in s.lower()],
                    "form": form
                })

def new(request):
    if request.method == "POST":
        form = NewArticleForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            article = form.cleaned_data["article"]
            if title not in util.list_entries():
                util.save_entry(title,article)
                return HttpResponseRedirect(reverse('article', args=[title]))
            else:
                # error
                print("Page already exists!")
    else:
        return render(request, "encyclopedia/new.html", {
            "form": SearchForm(),
            "new_form": NewArticleForm()
        })

def edit(request, title):
    if request.method == "POST":
        form = NewArticleForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            article = form.cleaned_data["article"]
            util.save_entry(title,article)
            return HttpResponseRedirect(reverse('article', args=[title]))
    else:
        article = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "title": title,
            "edit_form": NewArticleForm(initial={
                "title": title,
                "article": article
            })
        })
