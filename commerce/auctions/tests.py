from django.test import TestCase, Client
from django.db.models import Max

from .models import User, Listing, Bid, Comment, Category
# Create your tests here.

class AuctionTest(TestCase):

    def setUp(self):
        # create users
        test = User.objects.create_user(username='test', email='test@gmail.com', password='test1234')
        lbid = User.objects.create_user(username='lbid', email='lbid@gmail.com', password='lbid1234')

        # create listing
        Listing.objects.create(title='phone', description='description', price=100, owner=test)
        l2 = Listing.objects.create(title='', description='description2', price=200, owner=lbid)
        Listing.objects.create(title='phone3', description='description3', price=-100, owner=test)
        Listing.objects.create(title='phone4', price=0, owner=lbid)

        # create category
        Category.objects.create(category="Tools")
        Category.objects.create(category="Objects")
        Category.objects.create(category="Vetements")

        # create bid
        Bid.objects.create(item=l2, bidder=lbid, latest_price=300)

    def test_valid_listing(self):
        """Check the validity of listing"""

        l1 = Listing.objects.get(title='phone')
        self.assertTrue(l1.valid_listing())

    def test_invalid_listing_title(self):
        """Check the invalidity of listing by title"""

        l2 = Listing.objects.get(price=0)
        self.assertFalse(l2.valid_listing())
    
    def test_invalid_listing_price(self):
        """Check the invalidity of listing by price"""

        l3 = Listing.objects.get(title='phone3')
        self.assertFalse(l3.valid_listing())

        l4 = Listing.objects.get(title='phone4')
        self.assertFalse(l4.valid_listing())

    def test_user_listing_num(self):
        """Check the number of listing of a user"""

        u1 = User.objects.get(username="test")
        self.assertEqual(u1.items.count(), 2)

        u2 = User.objects.get(username="lbid")
        self.assertEqual(u2.items.count(), 2)

    def test_valid_bid(self):
        """Check the validity of a bid"""

        u1 = User.objects.get(username="lbid")
        l1 = Listing.objects.get(title='phone')

        b = Bid.objects.create(item=l1, bidder=u1, latest_price=101)

        self.assertTrue(b.valid_bid())

    def test_invalid_bid_sameUser(self):
        """Check the invalidity of a bid with the same user(owner and bidder)"""

        u1 = User.objects.get(username="test")
        l1 = Listing.objects.get(title='phone')

        b = Bid.objects.create(item=l1, bidder=u1, latest_price=101)

        self.assertFalse(b.valid_bid())
    
    def test_invalid_bid_invalidListing(self):
        """Check the invalidity of a bid with an invalid listing"""

        u1 = User.objects.get(username="lbid")
        l1 = Listing.objects.get(title='phone3')

        b = Bid.objects.create(item=l1, bidder=u1, latest_price=1000)

        self.assertFalse(b.valid_bid())

    def test_invalid_bid_invalidPrice(self):
        """Check the invalidity of a bid with an invalid bidding price(latest_price)"""

        u1 = User.objects.get(username="lbid")
        l1 = Listing.objects.get(title='phone')

        b = Bid.objects.create(item=l1, bidder=u1, latest_price=10)

        self.assertFalse(b.valid_bid())

    def test_num_bids(self):
        """Check the number of bids"""

        u1 = User.objects.get(username="lbid")
        l1 = Listing.objects.get(title='phone')
        u2 = User.objects.get(username="test")

        b = Bid.objects.create(item=l1, bidder=u1, latest_price=1000)
        b2 = Bid.objects.create(item=l1, bidder=u1, latest_price=1001)
        b3 = Bid.objects.create(item=l1, bidder=u2, latest_price=1002)

        i = Bid.objects.filter(item=l1)
        f = Bid.objects.filter(item=l1).first()
        # print('all the bids of u1 ',u1.bids.all())
        # print('all the bids of f.bidder 'f.bidder.bids.all())
        self.assertEqual(i.count(), 3)

    def test_user_num_bids(self):
        """Check the number of bids of a user"""
        
        u1 = User.objects.get(username="lbid")
        u2 = User.objects.get(username="test")
        l1 = Listing.objects.get(title='phone')
        
        b = Bid.objects.create(item=l1, bidder=u1, latest_price=1000)
        b2 = Bid.objects.create(item=l1, bidder=u1, latest_price=1001)
        b3 = Bid.objects.create(item=l1, bidder=u2, latest_price=1002)

        self.assertEqual(u1.bids.all().count(), 3)

    def test_valid_comment(self):
        """Chect the validity of a comment"""

        u1 = User.objects.get(username="lbid")
        u2 = User.objects.get(username="test")
        l1 = Listing.objects.get(title='phone')
        c = Comment.objects.create(item=l1, commentator=u1, comment="valid")
        c = Comment.objects.create(item=l1, commentator=u2, comment="success")

        self.assertTrue(c.valid_comment())
        self.assertEqual(Comment.objects.all().count(), 2)

    def test_invalid_comment(self):
        """Check the invalidity of a comment by invalid listing and no comment"""

        u1 = User.objects.get(username="lbid")
        u2 = User.objects.get(username="test")
        l1 = Listing.objects.get(title='phone')
        l2 = Listing.objects.get(title='phone4')

        c = Comment.objects.create(item=l1, commentator=u1)
        c2 = Comment.objects.create(item=l2, commentator=u2, comment="success")
    

        self.assertFalse(c.valid_comment())
        self.assertFalse(c2.valid_comment())

    def test_num_comments_user(self):
        """Check the number of comments of a user"""
        
        u1 = User.objects.get(username="lbid")
        u2 = User.objects.get(username="test")
        l1 = Listing.objects.get(title='phone')

        c = Comment.objects.create(item=l1, commentator=u1, comment="valid")
        c = Comment.objects.create(item=l1, commentator=u2, comment="success")
        c = Comment.objects.create(item=l1, commentator=u2, comment="woah")

        self.assertEqual(Comment.objects.filter(commentator=u2).all().count(), 2)

    def test_num_comments_listing(self):
        """Check the number of comments of a listing"""
        
        u1 = User.objects.get(username="lbid")
        u2 = User.objects.get(username="test")
        l1 = Listing.objects.get(title='phone')
        l2 = Listing.objects.get(title='phone3')

        c = Comment.objects.create(item=l1, commentator=u1, comment="valid")
        c = Comment.objects.create(item=l1, commentator=u2, comment="success")
        c = Comment.objects.create(item=l1, commentator=u2, comment="woah")
        c = Comment.objects.create(item=l2, commentator=u1, comment="valid")

        self.assertEqual(Comment.objects.filter(item=l1).all().count(), 3)
        self.assertNotIn(l2, Comment.objects.filter(item=l1).all())

    # Tests on the routes(views)
    
    def test_index(self):
        """"check the response of the index route(view) with its context"""
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["listings"].count(), 2)
        self.assertEqual(response.context["categories"].count(), 3)
        
        c.logout()

    def test_login(self):
        """"check the response httpRedirect(302) of the login route(view) with its context"""
        c = Client()
        response = c.post("/login", {"username": "test", "password": "test1234"})
        
        self.assertEqual(response.status_code, 302)
    
    def test_invalid_login(self):
        """"check the invalid response of the login route(view)"""
        c = Client()
        response = c.post("/login", {"username": "invalid", "password": "invalid1234"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "Invalid username and/or password.")
        
        c.logout()

    def test_invalid_login_by_get(self):
        """"check the invalid response of the login route(view) via get request"""
        c = Client()
        response = c.get("/login")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("auctions/login.html", [template.name for template in response.templates ])
        
        c.logout()

    def test_valid_registration(self):
        """"check the response httpRedirect(302) of the register route(view) with its context"""
        c = Client()
        response = c.post("/register", {"username": "new", "password": "new1234", 
                                        "confirmation": "new1234", "email": "new@gmail.com"})
        
        self.assertEqual(response.status_code, 302)
        
        c.logout()

    def test_invalid_registration_by_diffPass(self):
        """"check the invalid response of the registration route(view) by different password"""
        c = Client()
        response = c.post("/register", {"username": "new", "password": "new1234", 
                                        "confirmation": "new4321", "email": "new@gmail.com"})

        self.assertEqual(response.context["message"], "Passwords must match.")
        
    def test_invalid_registration_by_existUser(self):
        """"check the invalid response of the registration route(view) by existing user"""
        c = Client()
        response = c.post("/register", {"username": "test", "password": "test5678", 
                                        "confirmation": "test5678", "email": "new@gmail.com"})
        
        self.assertEqual(response.context["message"], "Username already taken.")

    def test_invalid_registration_by_get(self):
        """"check the invalid response of the registration route(view) via get request"""
        c = Client()
        response = c.get("/register")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("auctions/register.html", [template.name for template in response.templates ])
        
        c.logout()
    
    def test_valid_creation_listing(self):
        """"check the valid response (302) of the listing creation route(view)"""
        c = Client()
        c.login(username='test', password='test1234')
        response = c.post("/create", {"title": "desk", "description": "nice", 
                                        "price": "900", "img_url": "", "category": "1"})
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Listing.objects.filter(title="desk"))
        c.logout()
            
    def test_valid_creation_view_request(self):
        """"check the valid creation view of a listing"""
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/create")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["categories"].count(), 3)
        c.logout()

    def test_invalid_creation_listing(self):
        """"check the invalid response (302) of the listing creation route(view)"""
        c = Client()
        c.login(username='test', password='test1234')
        response = c.post("/create", {"title": "desk", "description": "nice", 
                                        "price": "900", "img_url": "", "category": "wrong"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "Sorry something went wrong!! Please try again.")
        c.logout()
    
    def test_valid_listing_view(self):
        """Check the valid response of a listing view."""

        c = Client()
        c.login(username='test', password='test1234')
        listing =Listing.objects.get(title='phone')
        response = c.get(f"/listing/{listing.id}")
        # print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["listing"], listing)
        c.logout()

    def test_invalid_listing_view(self):
        """Check the invalid listing resquests."""
        c = Client()
        
        c.login(username='lbid', password='lbid1234')
        listing = Listing.objects.all().aggregate(Max("id"))["id__max"]
        response = c.get(f"/listing/{listing + 1}")

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.context["message"], "404")
        c.logout()

        c = Client()
        
        c.login(username='lbid', password='lbid1234')
        response = c.get("/listing/listing")

        self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.context["message"], "404")
        c.logout()

    def test_unauthenticated_user_request_listing(self):
        """Check the unauthenticated user request of listing."""
        c = Client()
        c.login(username='wrong', password='wrong1234')
        listing = Listing.objects.get(title='phone')
        response = c.get(f"/listing/{listing.id}")

        self.assertEqual(response.status_code, 302)
        c.logout()
    
    def test_valid_bid_request(self):
        """Check the valid bid request."""

        c = Client()
        c.login(username='lbid', password='lbid1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/bid/{listing.id}", {"bid":"101"})
        
        u1 = User.objects.get(username="lbid")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bid.objects.filter(item=listing, bidder=u1))
        c.logout()
  
    def test_invalid_bid_request(self):
        """Check the invalid bid request by get"""
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.get(f"/bid/{listing.id}")
        
        self.assertEqual(response.status_code, 302)
        c.logout()
    
    def test_invalid_bidding_price(self):
        """Check the invalid bidding price responses."""
        
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/bid/{listing.id}", {"bid":"90"})
        
        self.assertEqual(response.status_code, 302)
        c.logout()
        
        # empty bid
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/bid/{listing.id}", {"bid":""})
        
        self.assertEqual(response.status_code, 302)
        c.logout()

        # wrong type(bid)
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/bid/{listing.id}", {"bid":"wrong"})
        
        self.assertEqual(response.status_code, 302)
        c.logout()

        # error latest_price > bid
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(price=200)
        response = c.post(f"/bid/{listing.id}", {"bid":"250"})
        
        self.assertEqual(response.status_code, 302)
        c.logout()
    
    def test_invalid_listing_bid(self):
        """Check the invalid listing of bid"""
        
        c = Client()
        c.login(username='test', password='test1234')
        max_id = Listing.objects.all().aggregate(Max('id'))["id__max"]
        response = c.post(f"/bid/{max_id + 1}", {"bid":"101"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        c.logout()

        # wrong type(listing)
        c = Client()
        c.login(username='test', password='test1234')
        max_id = Listing.objects.all().aggregate(Max('id'))["id__max"]
        response = c.post("/bid/wrong", {"bid":"101"})
        
        self.assertEqual(response.status_code, 404)
        c.logout()

    def test_valid_comment_request(self):
        """Check the valid comment request."""

        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/comment/{listing.id}", {"comment":"success"})
        
        self.assertEqual(response.status_code, 302)
        c.logout()

    def test_invalid_comment_request_method(self):
        """Check the invalid comment request method."""

        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.get(f"/comment/{listing.id}")
        
        self.assertEqual(response.status_code, 302)
        c.logout()

    def test_invalid_comment(self):
        """Check the invalid comment request."""

        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/comment/{listing.id}", {"comment":""})
        
        self.assertEqual(response.status_code, 302)
        c.logout()

    def test_invalid_comment2(self):
        """Check the valid comment request."""
        # unexisting listing
        c = Client()
        c.login(username='test', password='test1234')
        max_id = Listing.objects.all().aggregate(Max("id"))["id__max"]
        response = c.post(f"/comment/{max_id + 1}", {"comment":"success"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        c.logout()

        # wrong type(listing)
        c = Client()
        c.login(username='test', password='test1234')
        response = c.post(f"/comment/wrong", {"comment":"success"})
        
        self.assertEqual(response.status_code, 404)
        c.logout()

    def test_valid_watchlist_request(self):
        """Check the valid wacthlist request."""
        # add request
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/watchlist/{listing.id}", {"action":"add"})
        
        self.assertEqual(response.status_code, 302)
        c.logout()

        # remove request
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/watchlist/{listing.id}", {"action":"remove"})
        
        self.assertEqual(response.status_code, 302)
        c.logout()

    def test_invalid_watchlist_request(self):
        """Check the invalid wacthlist request."""

        # invalid method
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.get(f"/watchlist/{listing.id}")
        
        self.assertEqual(response.status_code, 302)
        c.logout()

        # unexisting listing
        c = Client()
        c.login(username='test', password='test1234')
        max_id = Listing.objects.all().aggregate(Max("id"))["id__max"]
        response = c.post(f"/watchlist/{max_id + 1}", {"action":"remove"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        c.logout() 

        # invalid type(listing)
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/watchlist/wrong", {"action":"remove"})
        
        self.assertEqual(response.status_code, 404)
        c.logout()

        # invalid action
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(title='phone')
        response = c.post(f"/watchlist/{listing.id}", {"action":"wrong"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "400 (error) Bad Request")
        c.logout()

    def test_MyWatchlists(self):
        """Get the user watchlists."""

        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/watchlists")
        
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["watchlists"].count(), 0)
        c.logout()

    def test_MyListings(self):
        """Get the user listings."""

        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/my_active_listings")
        u1 = User.objects.get(username="test")
        
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["auctions"].count(), 2)
        self.assertEqual(response.context["bids"].count(), 0)
        c.logout()

    def test_search(self):
        """Get a search."""

        # specific category
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/search", {"category": "1"})

        cat_name = Category.objects.get(pk=1)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], cat_name)
        self.assertEqual(response.context["listings"].count(), 0)
        self.assertEqual(response.context["categories"].count(), 3)
        c.logout()

        # all categories
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/search", {"category": "all"})

        cat_name = Category.objects.get(pk=1)
        
        self.assertEqual(response.status_code, 302)
        c.logout()

    def test_invalid_search(self):
        """Invalid search request"""
        # wrong category
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/search", {"category": "wrong"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        self.assertEqual(response.context["message"], "404")
        c.logout()

        # unexisting category
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/search", {"category": "100"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        self.assertEqual(response.context["message"], "404")
        c.logout()

        # no category
        c = Client()
        c.login(username='test', password='test1234')
        response = c.get("/search", {"category": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        self.assertEqual(response.context["message"], "404")
        c.logout()

    def test_listing_status(self):
        """Check listing status."""

        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(pk=1)

        # self.assertTrue(listing.status)

        response = c.post(f"/status/{listing.id}", {"action": "close"})

        # self.assertFalse(listing.status)
        self.assertEqual(response.status_code, 302)

        response = c.post(f"/status/{listing.id}", {"action": "activate"})
        
        self.assertTrue(listing.status)
        self.assertEqual(response.status_code, 302)

        c.logout()

    def test_invalid_status_request(self):
        """Invalid status request."""
        # invalid action
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(pk=1)

        response = c.post(f"/status/{listing.id}", {"action": "wrong"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        self.assertEqual(response.context["message"], "404")

        c.logout()

        # no action
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(pk=1)

        response = c.post(f"/status/{listing.id}", {"action": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        self.assertEqual(response.context["message"], "404")

        c.logout()

        # invalid listing
        c = Client()
        c.login(username='test', password='test1234')
        listing = Listing.objects.get(pk=1)

        response = c.post(f"/status/100", {"action": "activate"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "404 error")
        self.assertEqual(response.context["message"], "404")

        c.logout()
