from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, ReviewReport, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from cart.models import Item
from cart.regions import REGIONS


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    ratings = Rating.objects.filter(movie=movie)
    stats = ratings.aggregate(avg=Avg('value'), count=Count('id'))
    user_rating = None

    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['average_rating'] = (round(stats['avg'], 1)
        if stats['avg'] is not None else None)
    template_data['rating_count'] = stats['count']
    template_data['user_rating'] = user_rating
    template_data['star_range'] = range(1, 6)
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST' and request.POST.get('reason', '').strip():
        report = ReviewReport()
        report.review = review
        report.reported_by = request.user
        report.reason = request.POST['reason']
        report.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_reported_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user.is_staff:
        review.delete()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def top_commenters(request):
    if not request.user.is_staff:
        return redirect('movies.index')
    commenters = (Review.objects.values('user__username')
        .annotate(comment_count=Count('id'))
        .order_by('-comment_count','user__username')
    )
    template_data = {}
    template_data['title'] = 'Top Commenters'
    template_data['top_commenters'] = commenters
    template_data['top_commenter'] = commenters.first()
    return render(request, 'movies/top_commenters.html',
                  {'template_data': template_data})

def trending_map(request):
    sales = (Item.objects.filter(order__region__isnull=False)
        .values('order__region', 'movie__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('order__region', '-total_sold', 'movie__name')
    )
    regions = []
    for key, info in REGIONS.items():
        top_movies = [sale for sale in sales
            if sale['order__region'] == key][:3]
        regions.append({
            'name': info['name'],
            'lat': info['lat'],
            'lng': info['lng'],
            'movies': [{'name': sale['movie__name'],
                'total_sold': sale['total_sold']}
                for sale in top_movies],
        })
    template_data = {}
    template_data['title'] = 'Trending Map'
    template_data['regions'] = regions
    return render(request, 'movies/trending_map.html',
                  {'template_data': template_data})



@login_required
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    if request.method == 'POST':
        try:
            value = int(request.POST.get('value', ''))
        except ValueError:
            return redirect('movies.show', id=id)
        if 1<= value <= 5:
            Rating.objects.update_or_create(
                movie=movie, user=request.user,
                defaults={'value': value}
            )
    return redirect('movies.show', id=id)
