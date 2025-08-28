from django.contrib import admin
from .models import Visitor,Blog,User
# Register your models here.
admin.register(User)
admin.register(Visitor)

admin.register(Blog)
