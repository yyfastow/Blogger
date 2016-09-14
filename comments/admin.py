from django.contrib import admin

# Register your models here.
from comments import models

admin.site.register(models.Comment)
