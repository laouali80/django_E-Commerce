from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Bid, Listing, Comment, Category
from .forms import CreateForm, AddCommentForm
from django.shortcuts import redirect
from django.contrib import messages
from .templatetags.my_filter import usd
from django.utils import timezone


@login_required(login_url="/login")
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.exclude(owner=request.user).filter(status=True).order_by('-creationDate'),
        "categories": Category.objects.all()
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


def create_listing(request):
    # checking if the user trying to get the page is authenticated
    if request.user.is_authenticated:

        if request.method == "POST":
            # recuperation of the data first
            form = CreateForm(request.POST)

            #checking the validation of the form
            if form.is_valid():
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                price = form.cleaned_data["price"]
                endedDate = request.POST.get("endedDate", False)
                img_url = form.cleaned_data["img_url"]
                category = request.POST.get("category", False)

                #or
                # if "category" in request.POST:
                #     category = request.POST["category"]
                # else:
                #     category=False

                user = User.objects.get(pk=request.user.id)

               
                # Attempt to add the listing create
                try:
                    if category:
                        try:
                            if Category.objects.get(pk=int(category)):
                                item = Listing.objects.create(title=title, description=description, price=price, endedDate=endedDate,
                                                              img_url=img_url, owner=user, category=Category.objects.get(pk=int(category)))
                                item.save()
                        except IntegrityError and ValueError:
                            return render(request, "auctions/create_listing.html", {
                                "message": "Sorry something went wrong!! Please try again.",
                                "form": form
                            })
                    else:
                        item = Listing.objects.create(title=title, 
                                                      description=description, price=price, owner=request.user)
                        item.save()

                except IntegrityError or KeyError:
                    # print(e)
                    return render(request, "auctions/create_listing.html", {
                        "message": "Sorry something went wrong!! Please try again.",
                        "form": form
                    })

                return HttpResponseRedirect(reverse("index"))


        return render(request, "auctions/create_listing.html",{
            "form": CreateForm(),
            "categories": Category.objects.all()
        })

    return HttpResponseRedirect(reverse('login'))


def listing(request, listing_id):
    if request.user.is_authenticated:
        try:
            
            listing = Listing.objects.get(pk=int(listing_id))
        except UnboundLocalError or ValueError:
            raise Http404("Listing not found.")
        except Listing.DoesNotExist:
            return render(request, "errors/404.html", {
                "message": "404",
                "title": "404 error"
            })
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid": Bid.objects.filter(item=listing).order_by('-latest_price'),
                "form": AddCommentForm(),
                "comments": Comment.objects.filter(item=listing).order_by('-date'),
                "watchlist": listing in Listing.objects.filter(watchlist=request.user)
            })

    return HttpResponseRedirect(reverse('login'))


@login_required(login_url="/login")
def bid(request, listing_id):
    if request.method == "POST":
        bid = request.POST


        if not bid['bid'] or not bid['bid'].isdigit():
            messages.warning(request, 'This is warning. Please type a price to bid that is greater than the current bid if any or the initial price.')
            return redirect("listing", listing_id=listing_id)
        else:
            bid = int(bid["bid"])
        
        try:
            listing = Listing.objects.get(pk=int(listing_id))
        except UnboundLocalError or ValueError:
            raise Http404("Listing not found.")
        except Listing.DoesNotExist:
            return render(request, "errors/404.html", {
                "message": "404",
                "title": "404 error"
            })

        latest_price = Bid.objects.filter(item=listing).order_by('-latest_price')

        if latest_price:
            # getting the latest price as it is in a set
            latest_price = latest_price.first().latest_price

            if latest_price >= bid:
                messages.info(request, 'This is info. Please the bidding price must be greater than the current bid.')
                return redirect("listing", listing_id=listing_id)

            try:
                new_bid = Bid.objects.create(item=listing, bidder=request.user, latest_price=bid)

                messages.success(request, f'Confirmation. Your bid of {usd(bid)} on {(listing.title).title()} has been successful placed.')
                return redirect("listing", listing_id=listing_id)
            except:
                return render(request, "errors/400.html", {
                        "message": "400 Bad Request. The server cannot or will not process the request due to something that is perceived to be a client error.",
                        "title": "400 Bad Request",
                    })

        else:
            # save it if not biding yet

            # first check if the bid is greater than the initial price
            if listing.price < bid:

                try:
                    new_bid = Bid.objects.create(item=listing, bidder=request.user, latest_price=bid)

                    messages.success(request, f'Confirmation. Your bid of {usd(bid)} on {(listing.title).title()} has been successful placed.')
                    return redirect("listing", listing_id=listing_id)
                except:
                    return render(request, "errors/400.html", {
                            "message": "400 Bad Request. The server cannot or will not process the request due to something that is perceived to be a client error.",
                            "title": "400 Bad Request",
                        })
            else:
                messages.warning(request, 'This is warning. Please type a price to bid that is greater than the current bid if any or the initial price.')
                return redirect("listing", listing_id=listing_id)


    return redirect('listing', listing_id=listing_id )


@login_required(login_url="/login")
def comment(request, listing_id):
    if request.method == "POST":
        form = AddCommentForm(request.POST)

            #checking the validation of the form
        if form.is_valid():
            comment = form.cleaned_data["comment"]


            if not comment:
                return redirect("listing", listing_id=listing_id)

            try:
            
                listing = Listing.objects.get(pk=int(listing_id))
            except UnboundLocalError or ValueError:
                raise Http404("Listing not found.")
            except Listing.DoesNotExist:
                return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
            
            try:
                new_comment = Comment.objects.create(item=listing, 
                                                     commentator=request.user, comment=comment)

                return redirect("listing", listing_id=listing_id)
            except:
                return render(request, "errors/400.html", {
                        "message": "400 Bad Request. The server cannot or will not process the request due to something that is perceived to be a client error.",
                        "title": "400 Bad Request",
                    })
        else:
            return redirect('listing', listing_id=listing_id )
    else:
        return redirect('listing', listing_id=listing_id )


def watchlist(request, listing_id):
    if request.method == "POST":
        # data = request.POST
        action = request.POST["action"]

        if action == 'add':

            try:
            
                listing = Listing.objects.get(pk=int(listing_id))
            except UnboundLocalError or ValueError:
                raise Http404("Listing not found.")
            except Listing.DoesNotExist:
                return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
            
            listing.watchlist.add(request.user)
            messages.success(request, f'{(listing.title).title()} has been added to your watchlist.')
            return redirect('listing', listing_id=listing_id )
        elif action == 'remove':

            try:
            
                listing = Listing.objects.get(pk=int(listing_id))
            except UnboundLocalError or ValueError:
                raise Http404("Listing not found.")
            except Listing.DoesNotExist:
                return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
            
            listing.watchlist.remove(request.user)
            messages.info(request, f'{(listing.title).title()} has been removed to your watchlist.')
            return redirect('listing', listing_id=listing_id )
        else:
            # if the user submit something else rather than (add/remove), we throw a 400(bad request) error.
            return render(request, "errors/400.html", {
                    "message": "400",
                    "title": "400 (error) Bad Request"
                })

    else:
        # if the user attempt to access by a get request
        return redirect("index")

def my_watchlists(request):
    watchlists = Listing.objects.filter(watchlist=request.user)
    
    return render(request, "auctions/watchlists.html", {
                    "watchlists": watchlists
                })

def myActListings(request):
    # getting all the listing of the request user.
    my_act_listings = Listing.objects.filter(owner=request.user).order_by('-creationDate')

    return render(request, "auctions/my_act_listings.html", {
                    "auctions": my_act_listings,
                    "bids": Bid.objects.filter(bidder=request.user)
                })


def search(request):
    if request.method == "GET":
        search = request.GET.get("category", False)
        
        if search:
            # checking if the request is digit or numeric
            if search.isnumeric() and search.isdigit():
               
                try:
                    # checking if the category exists.
                    Category.objects.get(pk=int(search))
                        
                    return render(request, "auctions/search.html", {
                        "title": Category.objects.get(pk=int(search)),
                        "listings": Listing.objects.filter(status=True, 
                                                        category=Category.objects.get(pk=int(search))).order_by('-date'),
                        "categories": Category.objects.all()
                    })
                except UnboundLocalError or ValueError:
                    raise Http404("Listing not found.")
                except Category.DoesNotExist:
                    # if the category does not exist we throw a 404 (not found). error
                    return render(request, "errors/404.html", {
                        "message": "404",
                        "title": "404 error"
                    })
            # checking if the user wants all the auctions (with no category).
            elif search == "all":
                # print("all")
                return redirect("index")
            else:
                # else if the user attempt something else we throw a 404 (not found) error.
                return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
        else:
            return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
    else:
        # print("not here")
        # if the user attempt to access by a post request
        return redirect("index")

def status(request, listing_id):
    if request.method == "POST":
        action = request.POST.get("action", False)
        try:
            listing = Listing.objects.get(pk=int(listing_id))
        except UnboundLocalError or ValueError:
            raise Http404("Listing not found.")
        except Listing.DoesNotExist:
            # if the category does not exist we throw a 404 (not found). error
            return render(request, "errors/404.html", {
                "message": "404",
                "title": "404 error"
            })
        
        #checking if the action and listing exist
        if action and listing:
            if action == "close":
                
                listing.status=False
                listing.save()
                return redirect("listing", listing_id)
            elif action == "activate":
                
                listing.status=True
                listing.creationDate=timezone.now()
                listing.save()
                return redirect("listing", listing_id)
            else:
                # if neither of the above action, we throw a 404 (not found) error
                return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
        else:
            # else throw a 404 error (not found)
            return render(request, "errors/404.html", {
                    "message": "404",
                    "title": "404 error"
                })
    else:
        # if the user attempt to access by a get request
        return redirect("index")
        