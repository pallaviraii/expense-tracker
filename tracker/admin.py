from django.contrib import admin

from .models import Category, Transaction

admin.site.register(Category)
admin.site.register(Transaction)

admin.site.site_header = "PennyPilot Admin"
admin.site.site_title = "PennyPilot"
admin.site.index_title = "Welcome to PennyPilot"
