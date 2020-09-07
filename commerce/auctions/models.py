from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=100)
    url = models.TextField(max_length=100)
    category = models.CharField(max_length=20)
    min_bid= models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Bid(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=8, decimal_places=2)

class Comment(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class WatchlistItems(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE,related_name='listings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)