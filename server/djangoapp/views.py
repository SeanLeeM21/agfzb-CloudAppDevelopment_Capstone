from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .models import CarDealer, DealerReview, CarModel, CarMake
from .restapis import get_dealer_by_id_from_cf,get_dealer_reviews_from_cf,post_request, get_dealers_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def view(request):
    context = {} 
    # render function takes argument  - request
    # and return HTML as response
    return render(request, "index.html", context)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)
    
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['pword']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            # If not, return to login page again
            context["message"]="Username or password is incorrect."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    messages.success(request, ("You Were Logged Out!"))
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['pword']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to index page
            login(request, user)
            context["message"] = "Sign up successful!"
            return redirect('djangoapp:index')
        else:
            context["message"]="Account could not be created try again."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
'''def get_dealerships(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', context)'''

# Update the 'get_dealerships' view
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/fba3a4dc-6be1-43ac-87f1-3f7373d7ce28/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context = {}
        context["dealership_list"]=dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/fba3a4dc-6be1-43ac-87f1-3f7373d7ce28/dealership-package/get-dealership"
        apikey = "NMZMf5sVTPtKFdJcRsvtnei4tsTtHAlMDHEOZfG_8szb"
        dealer = get_dealer_by_id_from_cf(url, id)
        context["dealer"] = dealer
        context["id"]=id
    
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/fba3a4dc-6be1-43ac-87f1-3f7373d7ce28/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        context["reviews"] = reviews
        
        print(context)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, id):
    context = {}
    # If it is a GET request, just render the add_review page
    if request.method == 'GET':
        print("GET")
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/fba3a4dc-6be1-43ac-87f1-3f7373d7ce28/dealership-package/get-dealership"
        # Get dealers from the URL
        context = {
            "id": id,
            "dealer_name": get_dealer_by_id_from_cf(url, id).full_name,
            "cars": CarModel.objects.all()
        }
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        print("POST")
        if (request.user.is_authenticated):
            review = dict()
            review['id'] = 0
            review["name"]=request.POST["name"]
            review["dealership"]=id
            review["review"]=request.POST["content"]
            if ("purchasecheck" in request.POST):
                review["purchase"]=True
            else:
                review["purchase"]=False
            if review["purchase"] == True:
                car_parts=request.POST["car"].split("|")
                review["purchase_date"]=request.POST["purchase_date"] 
                review["car_make"]=car_parts[0]
                review["car_model"]=car_parts[1]
                review["car_year"]=car_parts[2]

            else:
                review["purchase_date"]=None
                review["car_make"]=None
                review["car_model"]=None
                review["car_year"]=None
            
            json_payload = {}
            json_payload["review"] = review
            json_result = post_request("https://us-south.functions.appdomain.cloud/api/v1/web/fba3a4dc-6be1-43ac-87f1-3f7373d7ce28/dealership-package/post-reviews", json_payload, id = id)
            print(json_result)
            if "error" in json_result:
                context["message"] = "ERROR: Review was not submitted."
            else:
                context["message"] = "Review was submited"
        else:
            print("User not authenticated")
        return redirect("djangoapp:dealer_details", id = id)

