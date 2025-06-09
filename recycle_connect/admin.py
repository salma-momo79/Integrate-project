from django.contrib import admin

# Register your models here.
from .models import Material, RecyclingCenter

admin.site.register(Material)
admin.site.register(RecyclingCenter)
