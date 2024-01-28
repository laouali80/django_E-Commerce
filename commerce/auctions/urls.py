from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("watchlists", views.my_watchlists, name="watchlists"),
    path("my_active_listings", views.myActListings, name="myActListings"),
    path("search", views.search, name="search"),
    path("status/<int:listing_id>", views.status, name="status"),
]
