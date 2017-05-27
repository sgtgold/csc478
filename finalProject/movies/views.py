from django.http import HttpResponse
from django.template import loader
from .models import Movies,Users
from star_ratings.models import Rating


def index(request):
    user_list = Users.objects.filter(userid = 1)
    movie_list = Movies.objects.filter(users__userid=1)

    ratings_list = user_list #GenericRelation(user_list[:5], related_query_name='ratings_list')
    template = loader.get_template('movies/index.html')

    context = {
        'movie_list': movie_list[:5],
        'user_list':user_list[:5],
        'ratings_list': ratings_list[:5]
    }
    return HttpResponse(template.render(context, request))