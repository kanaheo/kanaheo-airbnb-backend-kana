from django.contrib import admin
from .models import Photo, Viedo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass

@admin.register(Viedo)
class ViedoAdmin(admin.ModelAdmin):
    pass
