# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django_pandas.io import read_frame


class Movies(models.Model):
    movieId = models.IntegerField(default=0, unique=True)
    title = models.CharField(max_length=200)
    genres = models.CharField(max_length=200)

    class Meta:
        ordering = ['title']

class Users(models.Model):
    userId = models.IntegerField(default = 0,unique=True)

class CSVRatings(models.Model):
    userId = models.ForeignKey(Users, to_field="userId", db_column="userId")
    movies = models.ForeignKey(Movies, to_field="movieId", db_column="movieId")
    rating = models.FloatField(default = 0.0)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class Results(models.Model):
    users = models.ForeignKey(Users, to_field="userId", db_column="userId")
    movies = models.ForeignKey(Movies, to_field="movieId", db_column="movieId")
    estimate = models.FloatField(default = 0.0)
    