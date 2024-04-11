from django.contrib.auth.models import AbstractUser
from django.db import models
# from datetime import datetime
from django.utils import timezone

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    img_url = models.URLField(null=True, blank=True, default=None)
    status = models.BooleanField(default=True)
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='items')
    creationDate = models.DateTimeField(default=timezone.now)
    endedDate = models.DateTimeField()
    watchlist = models.ManyToManyField('User', blank=True, related_name='watchlist')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='categoried', null=True, blank=True)



    def __str__(self):
        return f"Item{self.id}"
    
    def valid_listing(self):
        if self.title and self.price > 0 and self.owner:
            return True
        else:
            return False

class Bid(models.Model):
    item = models.ForeignKey('Listing', on_delete=models.CASCADE)
    bidder = models.ForeignKey('User', on_delete=models.CASCADE, related_name="bids")
    latest_price = models.IntegerField()

    def __str__(self):
        return f"{self.id}: {self.item} bidded for {self.latest_price}"
    
    def valid_bid(self):
        if self.item.valid_listing() and self.item.price < self.latest_price and self.bidder != self.item.owner and self.bidder:
            return True
        else:
            return False


class Comment(models.Model):
    item = models.ForeignKey('Listing', on_delete=models.CASCADE)
    commentator = models.ForeignKey('User', on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"User {self.commentator} comments on {self.item}."
    
    def valid_comment(self):
        return self.item.valid_listing() and self.comment


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{(self.category).title()}"
