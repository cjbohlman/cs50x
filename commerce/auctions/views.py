from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, Bid, Comment, WatchlistItems

class NewListingForm(forms.Form):
    name = forms.CharField(min_length=1, max_length=20)
    description = forms.CharField(min_length=1, max_length=100, widget=forms.Textarea)
    url = forms.CharField(max_length=100)
    category = forms.CharField(max_length=20)
    min_bid = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01)
    # price = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01)

class NewBidForm(forms.Form):
    bid = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01)

class NewCommentForm(forms.Form):
    comment = forms.CharField(min_length=1, max_length=100)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.all()
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        new_form = NewListingForm(request.POST)
        if new_form.is_valid():
            name = new_form.cleaned_data["name"]
            description = new_form.cleaned_data["description"]
            url = new_form.cleaned_data["url"]
            category = new_form.cleaned_data["category"]
            min_bid = new_form.cleaned_data["min_bid"]
            price = new_form.cleaned_data["min_bid"]
            prev_named = AuctionListing.objects.get(name=name)
            if prev_named is None:
                return render(request, "auctions/create.html", {
                    "new_form":new_form,
                    "error": "Current active listing already has that name"
                })
            listing = AuctionListing.objects.create(name=name, description=description, url=url, category=category, min_bid=min_bid, price=price, user=request.user.username)
            listing.save()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_form": NewBidForm(),
                "comment_form": NewCommentForm()
            })
        else:
            pass
    else:
        return render(request, "auctions/create.html", {
            "new_form":NewListingForm()
        })

@login_required
def listing(request, listing_id):
    if request.method == "POST":
        bid_form = NewBidForm(request.POST)
        if bid_form.is_valid():
            new_price = bid_form.cleaned_data["bid"]
            listing_item = AuctionListing.objects.get(pk=listing_id)
            old_price = listing_item.price
            if new_price > old_price:
                listing_item.price = new_price
                listing_item.save()
                new_bid = Bid.objects.create(item=listing_id, user=request.user.username, bid=new_price )
                return render( request,"auctions/listing.html", {
                    "listing": listing_item,
                    "bid_form": NewBidForm(),
                    "comment_form": NewCommentForm()
                })
            else:
                return render(request,"auctions/listing.html", {
                    "listing": listing_item,
                    "bid_form": bid_form,
                    "error": "New bid must be higher than previous bid.",
                    "comment_form": NewCommentForm()
                })
        else:
            return render( request,"auctions/listing.html", {
                    "listing": listing_item,
                    "bid_form": bid_form,
                    "error": "Bid not valid.",
                    "comment_form": NewCommentForm()
                })
        
    else:
        listing_item = AuctionListing.objects.get(pk=listing_id)
        return render(request, "auctions/listing.html", {
            "listing": listing_item,
            "bid_form": NewBidForm(),
            "comment_form": NewCommentForm(),
            "comments": Comment.objects.filter(item=listing_id)
        })

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.cleaned_data["comment"]
            listing_item = AuctionListing.objects.get(pk=listing_id)
            new_comment = Comment.objects.create(comment=comment, user=User.objects.get(pk=request.user.id), item=listing_item)
            new_comment.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def watchlist(request):
    current_user = request.user.id
    items = WatchlistItems.objects.filter(user=current_user)
    print(items)
    return render(request, "auctions/watchlist.html", {
            "listings": items
        })

@login_required
def watchlist_add(request, listing_id):
    current_user = request.user.id
    new_wl_item = WatchlistItems.objects.create(user=User.objects.get(pk=request.user.id), item= AuctionListing.objects.get(pk=listing_id))
    new_wl_item.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))