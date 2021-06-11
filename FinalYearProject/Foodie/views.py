#importing necessary libraries
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Blogs, profile, Review
from .forms import UserUpdateForm, ProfileUpdateForm, UploadForm, ReviewForm, ContactForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import DetailView
from django.db.models import Avg
from django.http import JsonResponse
import numpy as np
import pandas as pd
import scipy as sp
import pymysql
from sklearn.neighbors import NearestNeighbors
import sqlalchemy
# Create your views here.

#Home page
def index(request):
    blog = Blogs.objects.order_by('-created_date')
    p = Paginator(blog, 9)
    page_number = request.GET.get('page', 1)
    page = p.page(page_number)
    context ={"Foodie_Blogs": page}      
    return render(request, "index.html", context)

#Signup/ Registration
def signup_page(request):
	return render(request, 'signup.html')

def signup(request):
	if request.method == 'POST':
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		username = request.POST['username']
		gmail = request.POST['gmail']
		password = request.POST['password']

		if User.objects.filter(username= username).exists():
			messages.error(request, 'Sorry!!! Username is already taken')
			return redirect('/signup_page/')

		elif User.objects.filter(email= gmail).exists():
			messages.error(request, 'Sorry!!! The account from this email is already made!')
			return redirect('/signup_page/')

		else:
			user= User.objects.create_user(first_name = firstname, last_name = lastname,email= gmail, username = username, password= password)
			user.save()
			messages.info(request, 'Account created succesfully.')
			return redirect('/login_page/')
	else:
		return render(request, '/signup_page/')

# login 
def login_page(request):
	return render(request, 'login.html')

@csrf_exempt
def login(request):
	if request.method == 'POST':
		login_username = request.POST['usernamelogin']
		login_password = request.POST['passwordlogin']

		user = auth.authenticate(username= login_username, password= login_password)
		
		if user is not None:
			auth.login(request, user)
			messages.success(request, 'User logged in.')
			return redirect('/')

		else:
			messages.error(request, 'Invalid username or password!! Try with correct one.')
			return redirect('/login_page/')

	else:
		return redirect('/login_page/')

#logout
def logout_view(request):
    logout(request)
    messages.success(request,"Successfully logged out")
    return redirect("index.html")

#contact form
def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            return redirect('/')
    return render(request, "email.html", {'form': form})


#profile
@login_required
def profile(request):
   if request.user.is_authenticated:
        user = request.user
        context ={} 
        context["Foodie_Blogs"] = Blogs.objects.filter(Author=request.user)
        user_posts = Blogs.objects.filter(Author=request.user).order_by('-created_date')
        return render(request, 'profile.html', {'Foodie_Blogs':user_posts,'user': user})
   else:
        return redirect('/login_page')

#updateprofile
@login_required
def updateprofile(request):
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST,
			                           request.FILES, instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.info(request, 'Successfully updated your profile!!!')
                return redirect('/profile')
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)
        context = {
			'u_form' : u_form,
			'p_form' : p_form
		}
        return render(request, 'updateprofile.html', context)

@login_required
#change Password
def passwordchange(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.info(request, 'Your password was successfully updated!')
            return redirect('/profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {
        'form': form
    })

def passwordresetdone(request):
	return render(request, 'password_change_done.html')

# create new post
@login_required
def create_post(request): 
    form = UploadForm()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.Author=request.user
            instance.save()
            messages.success(request, 'Successfully posted your blog!!!')
            return redirect('/profile')
	
    context ={'form': form} 
    return render(request, "view.html", context)
	

#detail post
def detail_post(request, pk): 
    data = Blogs.objects.get(id = pk) 
    reviews = Review.objects.filter(blog = pk).order_by('-pub_date')
    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    if average == None:
        average = 0
    average = round(average, 2)
    context={
        "data" : data,
        "reviews" : reviews,
        "average": average
    }
    return render(request, "detailpost.html", context) 

@login_required
def addreview(request, pk):
    data = Blogs.objects.get(id = pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():    
            review = form.save(commit=False)
            review.comment = request.POST["comment"]
            review.rating = request.POST["rating"]
            review.user = request.user
            review.blog = data
            review.save()
            #return render(request, 'detailpost.html')
            return redirect('/recommendations')      
    else:
        form = ReviewForm()
    context={'data' : data, 'form': form}
    return render(request, '/recommendations', context)


@login_required
def update_post(request, pk): 
    posts = Blogs.objects.get(id=pk) 
    form = UploadForm(instance = posts) 
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, instance = posts) 
        if form.is_valid(): 
            form.save() 
            messages.info(request, 'Successfully updated your blog!!!')
            return redirect('/profile')
    return render(request, "updatepost.html", { 'form' : form, 'posts': posts})
		
# delete view for details 
@login_required
def delete_post(request, pk): 
    context ={} 
    obj = get_object_or_404(Blogs, id = pk) 
  
  
    if request.method =="POST": 
        obj.delete()  
        return HttpResponseRedirect("/") 
  
    return render(request, "deleteview.html", context) 

#search page
def search(request):
    blog = Blogs.objects.all().order_by('-created_date')
    query = request.GET['query']
    if query:
       blog = Blogs.objects.filter(
	        Q(title__icontains=query)).distinct()
    paginator = Paginator(blog, 9)
    page_number = request.GET.get('page')

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    context ={"Foodie_Blogs": page} 
    return render(request, "search.html", context)
    return HttpResponse('This is search')

#KNN recommendation

def recommendation(request):
    num_reviews = Review.objects.count()
    all_user_names = list(map(lambda x: x.id, User.objects.only("id")))
    all_product_ids = set(map(lambda x: x.id, Blogs.objects.only("title")))
    num_users = len(list(all_user_names))
    print(num_users)
    Ratings_m = sp.sparse.dok_matrix((num_users, max(all_product_ids) + 1), dtype=np.float32)
    for i in range(num_users):  # each user corresponds to a row, in the order of all_user_names
        user_reviews = Review.objects.filter(user_id=all_user_names[i])
        for user_review in user_reviews:
            Ratings_m[i, user_review.blog_id] = user_review.rating

        Ratings = Ratings_m.transpose()

        coo = Ratings.tocoo(copy=False)
    df = pd.DataFrame({'title': coo.row, 'users': coo.col, 'rating': coo.data})[
        ['title', 'users', 'rating']].sort_values(['title', 'users']).reset_index(drop=True)

    mo = df.pivot_table(index=['title'], columns=['users'], values='rating')
    mo.fillna(3, inplace=True)
    model_knn = NearestNeighbors(algorithm='brute', metric='euclidean', n_neighbors=9)
    model_knn.fit(mo.values)
    distances, indices = model_knn.kneighbors((mo.iloc[14, :]).values.reshape(1, -1), return_distance=True)
    print(distances, indices)
    username= request.user.username
    context = list(map(lambda x: Blogs.objects.get(id=indices.flatten()[x]), range(0, len(distances.flatten()))))
    return render(request, 'recommendation.html', {'username': request.user.username,'context': context})


#import pickle to load the trained file
#content based recommendation
import pickle
@login_required
def content_based(request,pageno=1):
	new_obj = Blogs.objects.all()

	paginator = Paginator(new_obj, 9)
	no_of_pages = paginator.num_pages

	startpage = None

	if pageno < (no_of_pages-4):
		startpage = pageno
	else:
		startpage = (no_of_pages-4)

	endpage = startpage + 5
	pagelist = [i for i in range(startpage,endpage)]

	page_obj = paginator.get_page(pageno)
	context = {"blogs":page_obj,"pg":pagelist,"prev":startpage-1,"next":endpage+1}

	return render(request, 'SimilarityRecommendation.html', {"context":context})


def related(request,blog_id=-1):
	new_obj = return_related_food(blog_id)
	
	return render(request, 'Related.html', {"blogs":new_obj})

def return_related_food(blog_id):
	with open("train.pickle","rb") as f:
		cosine_sim = pickle.load(f)
	new_obj = Blogs.objects.all()
	food_list = []
	index_list = []
	for index,blog in enumerate(new_obj):
		food_list.append(blog.title)
		index_list.append(index)

	indices = pd.Series(index_list,index=food_list)
	print(indices.head(n=9))
	idx = indices[blog_id]
	scores = list(enumerate(cosine_sim[idx]))
	similarity_scores = sorted(scores, key=lambda x: x[1], reverse=True)
	similarity_scores = similarity_scores[:9]
	match_index = [i[0] for i in similarity_scores]
	print(match_index)
	blogs = []
	for index,blog in enumerate(new_obj):
		if index in match_index:
			blogs.append(blog)

	return blogs