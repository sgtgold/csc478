# Module Function
from surprise import KNNBasic
import os
from surprise import SVD
from surprise import Dataset
from surprise import evaluate, print_perf
import numpy as np
import pandas as pd
import operator
import surprise
from surprise import Reader

# creating a new dataset object
from surprise import dataset
from .models import CSVRatings


class MyDataset(dataset.DatasetAutoFolds):
    def __init__(self, df, reader):
        self.raw_ratings = [(uid, iid, r, timestamp) for (uid, iid, r, timestamp) in
                            zip(df['u'], df['i'], df['r'], df['t'])]
        self.reader = reader


# A function to convert pd dataframe to a Surprise object
def pdtoData(df):
    reader = Reader(line_format='user item rating timestamp', rating_scale=(1, 5))
    data = MyDataset(df, reader)
    return data


# entry will be a pd dataframe from web
# path is the place will the training set is stored
# Function to add new lines of rating entry to the training set
def addEntrytoTrain(data, entry):
    newmovie = data.append(pd.DataFrame(data=entry), ignore_index=True)
    newmovie.columns = ['u', 'i', 'r', 't']
    reader = Reader(line_format='user item rating timestamp', rating_scale=(1, 5))
    data = MyDataset(newmovie, reader)
    return data


##The function to predict and come up with the top 5 movies
def newUserRating(data, newuid, algo, movie):
    # Build an algorithm, and train it.
    trainset = data.build_full_trainset()
    algo.train(trainset)
    rating = {}
    movieId = movie.movieId
    movieId = list(movieId)
    for i in movieId:
        pred = algo.predict(newuid, i, r_ui=5, verbose=True)
        rating.update({i: pred.est})
    sorted_rating = sorted(rating.items(), key=operator.itemgetter(1))
    sorted_rating.reverse()
    watch = pd.DataFrame(data.raw_ratings, columns=['u', 'i', 'r', 't'])
    watched = watch[watch['u'] == newuid]
    for j in range(0, 20):
        for i in watched['i']:
            if sorted_rating[j][0] == i:
                sorted_rating.pop(j)
    ratings = np.array(sorted_rating[0:5])
    result = pd.DataFrame(ratings, columns=['movie_id', 'Estimate Rating'])
    return result

##Return the mean MAE and RMSE for CV results
def meanMetricsCV(algo,fold,data):
    data.split(n_folds=fold)
    algorithm=algo()
    perfsvd=evaluate(algorithm, data, measures=['RMSE', 'MAE'])
    MAE=sum(perfsvd['mae'])/fold
    RMSE=sum(perfsvd['RMSE'])/fold
    return MAE,RMSE
