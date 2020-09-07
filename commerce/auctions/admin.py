from django.contrib import admin

from .models import AuctionListing, Comment, Bid

# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "url", "category", "min_bid", "price", "user")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "user", "comment")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "user", "bid")

admin.site.register(AuctionListing, AuctionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)