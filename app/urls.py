from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('<int:id>/',views.home,name="home"),#home url doesn't require any id shows all blogs of all users either logged in or logged out
    path('user/', views.user_dashboard, name='user_dashboard'),#contains blogs and create blog options
    path('login/', views.user_login, name='login'),#redirect to user dashboard
    path('signup/', views.signup, name='signup'),#signup then try login
    path('create/', views.create_blog, name="create_blog"),#form asks title desc and image upload
    path('logout/',views.user_logout,name='logout'),
    path('',views.home,name="home"),
    path('pop/',views.pop,name="pop"),
    path('pop/<int:id>/',views.pop,name="pop"),
    path('delete_blog/<int:id>/', views.delete_blog, name='delete_blog'),
    
    #-------------admin routing--------
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('delete_user/<int:id>/',views.delete_user,name='delete_user'),
    path('health/', views.health_check, name='health-check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
