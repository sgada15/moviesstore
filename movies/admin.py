from django.contrib import admin
from .models import Movie, Review, ReviewReport, Rating

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(ReviewReport)
admin.site.register(Rating)