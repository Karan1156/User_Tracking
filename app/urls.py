from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home URLs
    path('', views.home, name="home"),  # Home without ID
    path('home/<int:id>/', views.home, name="home_with_id"), 
    path('blog/view/<int:id>/', views.view_blog, name='view_blog'),# Home with ID
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # User dashboard and blog management
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('create/', views.create_blog, name="create_blog"),
    path('edit/<int:id>/', views.create_blog, name="edit_blog"),  # Reuse create_blog view for editing
    path('delete/<int:id>/', views.delete_blog, name='delete_blog'),
    
    # Visitor tracking
    path('pop/', views.pop, name="pop_default"),  # Default pop without ID
    path('pop/<int:id>/', views.pop, name="pop"),  # Pop with user ID
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/delete-user/<int:id>/', views.delete_user, name='delete_user'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
