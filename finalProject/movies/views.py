from django.http import HttpResponseRedirect,HttpResponse
from django.template import loader,RequestContext
from .models import Movies,Users,CSVRatings,MovieFeatures
from django.shortcuts import render
from django.core.urlresolvers import reverse
from .recommender import newUserRating,pdtoData,meanMetricsCV
import pandas as pd
from surprise import SVD

from .forms import UserForm

def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            _user,created = Users.objects.get_or_create(userName=form.cleaned_data['user_name'])
            # redirect to a new URL:
            print created
            if created:
                print 'New User'
                url = reverse('UserMovieListForm', kwargs={'id': _user.id})
            else:

                ratings = CSVRatings.objects.all().filter(user=_user)
                if len(ratings) >= 3:
                    print 'Existing User'
                    url = reverse('recommendations', kwargs={'id': _user.id})
                else:
                    url = reverse('UserMovieListForm', kwargs={'id': _user.id})
            return HttpResponseRedirect(url)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()

    return render(request, 'movies/user.html', {'form': form})

def add_movie(request,id):
    template = loader.get_template('movies/addmovie.html')
    movies_list_1 = Movies.objects.all().order_by('title')
    context = {
        'movie_list_1': movies_list_1,
    }
    if request.method == 'POST':
        template = loader.get_template('movies/recommendations.html')
        userid = id
        _user = Users.objects.get(id=userid)
        print 'User to be passed:', _user
        url = reverse('recommendations', kwargs={'id': _user.id})
        return HttpResponseRedirect(url)
    else:
        print "Load"
    return HttpResponse(template.render(context, request))



def user_movies(request, id):
    template = loader.get_template('movies/initialpicks.html')
    movies_list_1 = Movies.objects.all().order_by('title')
    movies_list_2 = Movies.objects.all().order_by('title')
    movies_list_3 = Movies.objects.all().order_by('title')
    context = {
        'movie_list_1': movies_list_1,
        'movie_list_2': movies_list_2,
        'movie_list_3': movies_list_3,
    }
    if request.method == 'POST':

        userid = id
        _user = Users.objects.get(id=userid)
        m1 = request.POST['movie1']
        m2 = request.POST['movie2']
        m3 = request.POST['movie3']
        #Non-Valid Post
        if(m1 == m2 or m1 == m3 or m2 == m3):
            context = {
                'movie_list_1': movies_list_1,
                'movie_list_2': movies_list_2,
                'movie_list_3': movies_list_3,
                'error_message' : 'No duplicate movies allowed',
            }
            return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('movies/recommendations.html')
            #Submit new ratings
            CSVRatings.objects.get_or_create(user=_user,movies=Movies.objects.get(movieId=m1),rating=request.POST['rating1'])
            CSVRatings.objects.get_or_create(user=_user, movies=Movies.objects.get(movieId=m2),rating=request.POST['rating2'])
            CSVRatings.objects.get_or_create(user=_user, movies=Movies.objects.get(movieId=m3),rating=request.POST['rating3'])
            print 'User to be passed:', _user
            url = reverse('recommendations', kwargs={'id': _user.id})
            return HttpResponseRedirect(url)
    else:
        print "Load"
    return HttpResponse(template.render(context, request))


class MovieRecs:
    def __init__(self,rank, title,pred_rating):
        self.rank = rank
        self.title = title
        self.pred_rating = pred_rating

def recommend_movies(request,id):
    if request.method == 'GET':
        template = loader.get_template('movies/recommendations.html')
        #ratings = pd.DataFrame(CSVRatings.objects.all().values_list('movies_id','user_id','rating'))
        ratings = pd.DataFrame(list(CSVRatings.objects.all().values()))
        ratings = ratings.drop('id',1)
        ratings = ratings[['user_id','movies_id','rating','timestamp']]
        ratings['u'] = ratings['user_id']
        ratings['i'] = ratings['movies_id']
        ratings['r'] = ratings['rating']
        ratings['t'] = ratings['timestamp']

        ratings = ratings.drop('user_id',1)
        ratings = ratings.drop('movies_id', 1)
        ratings = ratings.drop('rating', 1)
        ratings = ratings.drop('timestamp', 1)

        movies_list = Movies.objects.all()
        movie_df = pd.DataFrame(list(Movies.objects.values_list('movieId',flat=True)),columns=['movieId'])

        data = pdtoData(ratings)
        result = newUserRating(data, float(id), SVD(), movie_df)

        m_list = []
        for index,row in result.iterrows():
            print row
            movie = Movies.objects.get(movieId=int(row['movie_id']))
            m = MovieRecs(rank=index+1,title= movie.title,pred_rating = row['Estimate Rating'])
            m_list.append(m)
        context = {
            'movie_list':m_list
        }
    if request.method == 'POST':
        url = reverse('addMovieForm', kwargs={'id': id})
        return HttpResponseRedirect(url)
    return HttpResponse(template.render(context, request))

def admin(request):
    user_list = Users.objects.all()
    movies_list = Movies.objects.all()
    csvmovies_list = CSVRatings.objects.order_by().values_list('movies_id', flat=True).distinct()
    ratings_list = CSVRatings.objects.order_by().values_list('rating', flat=True)
    template = loader.get_template('movies/admin.html')
    summaryList = []

    ratings = pd.DataFrame(list(CSVRatings.objects.all().values()))
    ratings = ratings.drop('id', 1)
    ratings = ratings[['user_id', 'movies_id', 'rating', 'timestamp']]
    ratings['u'] = ratings['user_id']
    ratings['i'] = ratings['movies_id']
    ratings['r'] = ratings['rating']
    ratings['t'] = ratings['timestamp']

    ratings = ratings.drop('user_id', 1)
    ratings = ratings.drop('movies_id', 1)
    ratings = ratings.drop('rating', 1)
    ratings = ratings.drop('timestamp', 1)

    movies_list = Movies.objects.all()
    movie_df = pd.DataFrame(list(Movies.objects.values_list('movieId', flat=True)), columns=['movieId'])

    data = pdtoData(ratings)

    summary.numUsers = len(user_list)
    summary.numMovies = len(movies_list)
    summary.avgMovies = len(csvmovies_list)/summary.numUsers
    summary.avgRating = sum(ratings_list)/len(ratings_list)
    summary.newUser=max(ratings['u'])-671
    movie_df = pd.DataFrame(list(csvmovies_list), columns=['movieId'])
    #summary.MAE,summary.RMSE=meanMetricsCV(SVD,5,data)
    summary.MAE=0.690496627721
    summary.RMSE=0.898839313311

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

def histGenre1(request):

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    import pandas as pd
    import numpy as np

    fig = Figure()
    rdf = pd.Series(MovieFeatures.objects.filter(Genre1__in=['Action','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Horror','Music','Musical','Mystery','Romance','Sci-Fi','Short','Thriller','War','Western']).values().values_list('Genre1', flat=True))
    ax = fig.add_subplot(111)
    labels = ['Action','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Horror','Music','Musical','Mystery','Romance','Sci-Fi','Short','Thriller','War','Western']
    gData = np.array(rdf.value_counts())#.plot(kind='bar')
    print gData

    ax.bar(left=np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]),height=gData)
    ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,20,21])

    ax.set_title('Count of Movies by Genre')
    ax.set_ylabel('Genre Count')
    ax.set_xlabel('Genre')

    ax.set_xticklabels(labels,rotation=90)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def histProd(request):

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
    fig = Figure()
    rdf = pd.Series(MovieFeatures.objects.filter(Production__in=['Sony Pictures','Universal Pictures','Paramount Pictures','20th Century Fox','Warner Bros.']).values().values_list('Production', flat=True))

    ax = fig.add_subplot(111)
    labels = ['Sony Pictures','Universal Pictures','Paramount Pictures','20th Century Fox','Warner Bros.']
    gData = np.array(rdf.value_counts())#.plot(kind='bar')

    ax.bar(left=np.array([0,1,2,3,4]),height=gData)
    ax.set_xticks([0,1,2,3,4,5])
    ax.set_title('Count of Movies by Major Production Companies')
    ax.set_ylabel('Movie Count')
    ax.set_xlabel('Production Companies')

    ax.set_xticklabels(labels, rotation=45)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def histYear(request):

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
    fig = Figure()
    rdf = pd.Series(MovieFeatures.objects.filter(Year__in=['2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']).values().values_list('Year', flat=True))

    ax = fig.add_subplot(111)
    labels = ['2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']
    gData = np.array(rdf.value_counts())#.plot(kind='bar')
    
    ax.bar(left=np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]),height=gData)
    ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
    ax.set_title('Count of Movies by Year (21st Century)')
    ax.set_ylabel('Movie Count')
    ax.set_xlabel('Year')

    ax.set_xticklabels(labels, rotation=45)
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