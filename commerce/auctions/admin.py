from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category

# Register your models here.

class ListingsAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

admin.site.register(User)
admin.site.register(Listing, ListingsAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
