import os
from surprise import dataset,SVD,KNNBasic,evaluate, print_perf,Reader
import numpy as np
import pandas as pd
import operator

class MyDataset(dataset.DatasetAutoFolds):

    def __init__(self, df, reader):

        self.raw_ratings = [(uid, iid, r, timestamp) for (uid, iid, r, timestamp) in
                            zip(df['u'], df['i'], df['r'],df['t'])]
        self.reader=reader