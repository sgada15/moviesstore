from django.contrib import admin
from django.db.models import Count, Max, Sum
from django.template.response import TemplateResponse
from django.urls import path
from .models import Movie, Review, ReviewReport

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

    def get_urls(self):
        return [
            path('popularity/', self.admin_site.admin_view(self.popularity),
                 name='movies_movie_popularity'),
        ] + super().get_urls()

    @staticmethod
    def top_movies(metric):
        movies = Movie.objects.annotate(total=metric).filter(total__gt=0)
        maximum = movies.aggregate(maximum=Max('total'))['maximum']
        if maximum is None:
            return Movie.objects.none()
        return movies.filter(total=maximum).order_by('name', 'pk')

    def popularity(self, request):
        # Separate queries prevent reviews from multiplying purchase totals.
        context = {
            **self.admin_site.each_context(request),
            'title': 'Movie popularity',
            'purchase_leaders': self.top_movies(Sum('item__quantity')),
            'review_leaders': self.top_movies(Count('review')),
        }
        return TemplateResponse(request, 'admin/movies/movie/popularity.html',
                                context)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(ReviewReport)
