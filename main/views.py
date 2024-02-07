from django.shortcuts import render, redirect
from . import models
from django.contrib.auth.models import User
from django.contrib.auth import  login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# FRONT
def index(request):
    categories = models.Category.objects.all()
    products = models.Product.objects.all()
    user = request.user
    is_liked  = []
    for product in products:
        try:
            liked = models.Wishlist.objects.filter(product_id=product.id, user=user).exists()
        except models.Wishlist.DoesNotExist:
            liked = None
        is_liked.append(liked)
    product_items = zip(products, is_liked)

    context = {
        'categories': categories,       
        'product_items': product_items,
        'user':user,
        'is_liked': is_liked
    }
    return render(request, 'front/index.html', context)

def like_in_index(request, id):
    user = request.user
    wishlist_product = models.Product.objects.get(id=id)
    models.Wishlist.objects.create(
        user=user,
        product=wishlist_product
    )
    return redirect('index')

def dislike_in_index(request, id):
    user = request.user
    disliked = models.Wishlist.objects.filter(product_id=id, user=user)
    disliked.delete()
    return redirect('index')



def products(request):
    products = models.Product.objects.all()
    return render(request, 'front/products.html', {'products': products, 'user': request.user})

def product_detail(request, id):
    user = request.user
    # wishlist_product = models.Wishlist.objects.get(product_id=id, user=user)
    try:
        is_liked = models.Wishlist.objects.filter(product_id=id, user=user)
    except models.Wishlist.DoesNotExist:
        is_liked = None
    product = models.Product.objects.get(id=id)
    images = models.ProductImage.objects.filter(product_id=product.id)
    categories = models.Category.objects.all()
    recommendations = models.Product.objects.filter(
        category_id=product.category.id).exclude(id=product.id)[:3]
    
    review = product.review
    
    # product = models.ProductReview.objects.get(product_id=id, user=user)
    # if user != product.user:
    #     product.mark = request.POST['mark']
    # product.save()
    context = {
        'product': product,
        'images': images,
        'categories': categories,
        'recommendations' : recommendations,
        'review': range(review),
        'user': request.user,
        'is_liked': is_liked
        
    }
    
    return render(request, 'front/product_detail.html', context)


def blog(request):
    return render(request, 'front/blog.html', {'user': request.user})

def contact(request):
    return render(request, 'front/contact.html', {'user': request.user})

def sorted_products(request, id):
    categories = models.Category.objects.all()
    products = models.Product.objects.all()
    sorted_products = models.Product.objects.filter(category_id=id)
    if sorted_products.exists():
        category = sorted_products.first().category
    else:
        category = None
    context = {
        'categories': categories,
        'products': products,
        'sorted_products': sorted_products,
        'category':category,
        'user': request.user
    }
    return render(request, 'front/sorted_products.html', context)

def like_in_detail(request, id):
    user = request.user
    wishlist_product = models.Product.objects.get(id=id)
    models.Wishlist.objects.create(
        user=user,
        product=wishlist_product
    )
    return redirect('product_detail', id=id)

def dislike_in_detail(request, id):
    user = request.user
    disliked = models.Wishlist.objects.filter(product_id=id, user=user)
    disliked.delete()
    return redirect('product_detail', id=id)


@login_required
def carts(request):
    actives = models.Cart.objects.filter(is_active=True, user=request.user)
    inactives = models.Cart.objects.filter(is_active=False, user=request.user)
    context = {
        'actives': actives,
        'inactives': inactives,
        'user': request.user
    }
    return render(request, 'front/cart/carts.html', context)    

@login_required
def cart_detail(request, id):
    cart = models.Cart.objects.get(id=id)
    items = models.CartProduct.objects.filter(cart=cart)
    context = {
        'cart': cart, 
        'items': items,
        'user': request.user
    }
    return render(request, 'front/cart/cart_detail.html', context)

# @login_required
# def add_to_cart(request, id):
#     user = request.user
#     if request.method == 'POST':
#         cart = models.Cart.objects.get(user=user)
#         if cart:
#             quantity = models.Product.objects.get(id=id).quantity
#             models.Cart.objects.create(
#                 cart=cart,
#                 quantity=quantity
#             )
        
@login_required
def give_review(request, id):
    user = request.user
    product = models.ProductReview.objects.get(product_id=id, user=user)
    # print(product.user)
    product.mark = request.POST['rate']
    product.save()


# Authentication    
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User



def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        try:
            # Check if the username already exists
            existing_user = User.objects.get(username=username)
            return render(request, 'front/register.html', {'error_message': 'Username already exists'})
        except User.DoesNotExist:
            pass

        # Check if passwords match
        if password != confirm_password:
            return render(request, 'front/register.html', {'error_message': 'Passwords do not match'})

        try:
            # Create the user
            user = User.objects.create_user(username=username, password=password)
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        except Exception as e:
            return render(request, 'front/register.html', {'error_message': f'Error creating user: {str(e)}'})

    return render(request, 'front/register.html', {'user': request.user})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user =  authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'front/account.html', {'error_message': 'Invalid username or password', 'user': request.user})
        
def my_account(request):
    user =request.user
    if request.user.is_authenticated:
        username = request.user.username
        password = request.user.password
        context = {
            'username': username,
            'password': password
        }
        return render(request, 'front/user_details.html', context)
    else:
        return render(request, 'front/account.html', {'user': user})
    
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        new_username = request.POST['username']
        new_password = request.POST['password']

        
        if new_username != user.username and User.objects.filter(username=new_username).exists():
            messages.error(request, 'Username is already taken. Please choose another one.')
            return redirect('edit_profile')  

        user.username = new_username

        if new_password:
            user.set_password(new_password)
            update_session_auth_hash(request, user) 

        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('my_account')
    return render(request, 'front/user_details.html', {'user': user})

            

def logout_user(request):
    logout(request)
    return redirect('index')


# DASHBOARD
def dashboard(request):
    return render(request, 'dashboard/index.html')


 # dashboard/category
def category_list(request):
    categories = models.Category.objects.all()
    return render(request, 'dashboard/category/list.html', {'categories':categories})

def create_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        models.Category.objects.create(name=name)
        return redirect('category_list')
    return render(request, 'dashboard/category/create.html')

def update_category(request, id):
    category = models.Category.objects.get(id=id)
    # print(id)
    ctg = request.POST.get('name', '')  # Using get method with a default value ('') to avoid MultiValueDictKeyError
    if ctg:
        category.name = ctg
        category.save()
        return redirect('category_list')
    return render(request, 'dashboard/category/update.html', {'category': category})


def delete_category(request, id):
        models.Category.objects.get(id=id).delete()
        return redirect('category_list')


 # dashboard/product
def product_list_dashboard(request):
    products = models.Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'dashboard/product/list.html', context)

def create_product(request):
    # users = [user.username for user in models.User.objects.all()]
    user = request.user
    categories = models.Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        quantity = request.POST['quantity']
        price = request.POST['price']
        currency = request.POST['currency']
        baner_image = request.FILES.get['baner_image']
        images = request.FILES.getlist['images']
        category = request.POST['category']
        # print(images)
        # print(f"BANER {baner_image}")
        if request.POST["discount_price"]:
            discount_price = request.POST["discount_price"]
        # try:
        #     if request.POST['creator'] in users:
        #         creator = models.User.objects.get(username=request.POST['creator'])  
        #     else:
        #         raise ValueError("Creator specified does not match the logged-in user")
        # except models.User.DoesNotExist:
        #     return HttpResponse("Error: Creator specified does not exist", status=400)
        # except Exception as e:
        #     return HttpResponse("Error: " + str(e), status=400)
        product = models.Product.objects.create(
            name=name,
            description=description,
            quantity=quantity,
            price=price,
            currency=currency,
            discount_price=discount_price,
            baner_image=baner_image,
            category=category,
            creator=user.username
        )
        for image in images:

            models.ProductImage.objects.create(
                images=image, 
                product=product
            )
        return redirect("product_list_dashboard")
    return render(request, 'dashboard/product/create.html', { 'categories': categories})






            
    




