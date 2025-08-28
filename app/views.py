from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Visitor, Blog
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BlogForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import user_passes_test
import json
import requests
from django.utils.dateformat import DateFormat
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.core.serializers.json import DjangoJSONEncoder
import cloudinary.uploader
from django.db import connection
from django.db.models import Count


def health_check(request):
    # Optional: check DB
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_ok = True
    except:
        db_ok = False

    status = "ok" if db_ok else "error"
    return JsonResponse({
        "status": status,
        "db_connection": db_ok,
        "message": "Server is healthy" if db_ok else "Database connection failed"
    })


def home(request, id=None):
    if id:
        return redirect('pop', id=id)  # Use URL name instead of hardcoded path
    blogs = Blog.objects.all().order_by('-id')
    return render(request, 'home.html', {'blogs': blogs})


def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Signup successful! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


def user_login(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already logged in no need to login")
        return redirect('user_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password. Try again.")
            return redirect('login')

    return render(request, 'login.html')


def signup(request):
    if request.user.is_authenticated:
        messages.error(request, " You are already logged in no need to create account! ")
        return redirect('user_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Signup successful! Please log in.")
            return redirect('login')

    return render(request, 'signup.html')

@login_required
def user_dashboard(request):
    try:
        # Get visitor counts by date
        visitor_counts = Visitor.objects.filter(user=request.user) \
            .annotate(date_only=TruncDate('date')) \
            .values('date_only') \
            .annotate(count=Count('id')) \
            .order_by('date_only')
        
        # Extract dates and counts
        dates = [v['date_only'].strftime('%Y-%m-%d') for v in visitor_counts]
        counts = [v['count'] for v in visitor_counts]
        
        # Get user's blogs
        blogs = Blog.objects.filter(author=request.user)
        
        # Get all visitors for this user with location data
        visitors = Visitor.objects.filter(user=request.user).order_by('-date')
        
        # Prepare visitor data for JSON serialization
        visitors_data = []
        for visitor in visitors:
            visitors_data.append({
                'name': visitor.name,
                'latitude': float(visitor.latitude) if visitor.latitude else None,
                'longitude': float(visitor.longitude) if visitor.longitude else None,
                'date': visitor.date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Count visitors with location data
        visitors_with_location = Visitor.objects.filter(
            user=request.user, 
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        
        # Get recent visitors (last 10)
        recent_visitors = visitors[:10]
        
        # Pass the data to the template
        return render(request, 'user_dashboard.html', {
            'visitor_dates': json.dumps(dates),
            'visitor_counts': json.dumps(counts),
            'id': request.user.id,
            'blogs': blogs,
            'visitors_json': json.dumps(visitors_data),
            'recent_visitors': recent_visitors,
            'total_visitors': visitors.count(),
            'visitors_with_location': visitors_with_location,
        })
    except Exception as e:
        # Log the error for debugging
        print(f"Error in user_dashboard: {e}")
        # Fallback without visitor data
        blogs = Blog.objects.filter(author=request.user)
        return render(request, 'user_dashboard.html', {
            'visitor_dates': json.dumps([]),
            'visitor_counts': json.dumps([]),
            'id': request.user.id,
            'blogs': blogs,
            'visitors_json': json.dumps([]),
            'recent_visitors': [],
            'total_visitors': 0,
            'visitors_with_location': 0,
        })
@login_required
def create_blog(request, id=None):
    if id:
        blog = get_object_or_404(Blog, pk=id, author=request.user)
        form = BlogForm(request.POST or None, request.FILES or None, instance=blog)
    else:
        form = BlogForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, "Blog saved successfully!")
            return redirect('user_dashboard')
    
    return render(request, 'upload.html', {'form': form})


@login_required
def delete_blog(request, id):
    # Get the blog object (or return 404 if not found)
    blog = get_object_or_404(Blog, id=id, author=request.user)
    
    blog.delete()  # Delete the blog
    messages.success(request, "Blog deleted successfully!")
    return redirect('user_dashboard')


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# ------------------------ admin dashboard ---------------------------
def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.annotate(blog_count=Count('blog'))
    
    # Use proper date formatting
    signup_dates = [user.date_joined.strftime('%Y-%m-%d') for user in users]
    signup_dates_json = json.dumps(signup_dates)

    context = {
        'users': users,
        'user_signup_dates': signup_dates_json,
    }

    return render(request, 'admin_dashboard.html', context)


@user_passes_test(is_admin)
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
        user.delete()
        messages.success(request, "User deleted successfully!")
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
    return redirect('admin_dashboard')


# --------------------- fetching data from the visitor -------------------------------
def get_public_ip(request):
    # Get the user's public IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
    return ip


def get_location(ip):
    # Use ipinfo.io to get the location based on the IP address
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=5)
        data = response.json()
        return data.get('loc')  # This returns a string like "latitude,longitude"
    except:
        return None


def pop(request, id=None):
    if id is None:
        # Handle case where no ID is provided
        messages.error(request, "No user specified.")
        return redirect('home')
        
    if request.method == 'POST':
        name = request.POST.get('name')  # Use request.POST to get form data
        if name:  # Check if name is provided
            ip = get_public_ip(request)  # Get the user's IP address
            location = get_location(ip)  # Get the location based on the IP

            if location:
                try:
                    latitude, longitude = location.split(',')  # Split the location string
                except:
                    latitude, longitude = None, None
            else:
                messages.error(request, "Could not retrieve location data.")
                return redirect('home')  # Redirect to home or another page

            # Save visitor data
            try:
                user = User.objects.get(id=id)
                vis = Visitor(user=user, name=name, longitude=longitude, latitude=latitude)
                vis.save()
                messages.success(request, "Visitor data saved successfully.")
                return redirect('user_dashboard')  # Redirect after saving
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect('home')

    return render(request, 'pop.html')
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def view_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    
    # Debug: Check if template exists
    try:
        template = get_template('view_blog.html')
        print("Template found!")
    except TemplateDoesNotExist:
        print("Template not found!")
        # List directories Django is searching
        from django.template.loaders.filesystem import Loader as FilesystemLoader
        from django.template.loaders.app_directories import Loader as AppLoader
        
        print("Filesystem loader directories:", FilesystemLoader.get_dirs())
        print("App loader directories:", AppLoader.get_dirs())
    
    return render(request, 'view_blog.html', {'blog': blog})






