from django.http import HttpResponse
from django.template import loader
from .models import Movies,Users,CSVRatings,MovieFeatures
from star_ratings.models import Rating
from django.shortcuts import render

from .forms import UserForm

def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()

    return render(request, 'movies/newuser.html', {'form': form})

def admin(request):
    user_list = Users.objects.all()
    movies_list = Movies.objects.all()
    csvmovies_list = CSVRatings.objects.order_by().values_list('movies_id', flat=True).distinct()
    ratings_list = CSVRatings.objects.order_by().values_list('rating', flat=True)
    template = loader.get_template('movies/admin.html')
    summaryList = []

    summary.numUsers = len(user_list)
    summary.numMovies = len(movies_list)
    summary.avgMovies = len(csvmovies_list)/summary.numUsers
    summary.avgRating = sum(ratings_list)/len(ratings_list)

    summaryList.append(summary)
    context = {
        'summaryList':summaryList,
    }
    return HttpResponse(template.render(context, request))
def index(request):
    template = loader.get_template('movies/index.html')
    context = {

    }
    return HttpResponse(template.render(context, request))

#Number of Movies by Length
def histRated(request):

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    import pandas as pd
    import numpy as np

    fig = Figure()
    rdf = pd.Series(MovieFeatures.objects.filter(Rated__in=['R','PG-13','PG','G']).values().values_list('Rated', flat=True))

    ax = fig.add_subplot(111)
    labels = ['R','PG-13','PG','G']
    gData = np.array(rdf.value_counts())#.plot(kind='bar')

    ax.bar(left=np.array([0,1,2,3]),height=gData)
    ax.set_xticks([0,1,2,3,4])

    ax.set_title('Count of Movies by Rating')
    ax.set_ylabel('Movie Count')
    ax.set_xlabel('Rating')

    ax.set_xticklabels(labels)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

#Template
def simple(request):
    import random
    import datetime

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter


    fig = Figure()
    ax = fig.add_subplot(111)
    x = []
    y = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now += delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
#Number of Users
#Number of Movies
#Average Movies seen per User
#Average Rating
#New Users since launch
class summary:
    numUsers = 0
    numMovies = 0
    avgMovies = 0
    avgRating = 0