from __future__ import absolute_import, unicode_literals

from django.utils.timezone import now
from datetime import datetime, timedelta
from .models import CategoryRating, BookRating, Book, Categories, Reccomendation
from django.contrib.auth.models import User
from django.utils import timezone
import pandas as pd
import numpy as np
from books.celery import app
from celery.task import task


class RecomendationCategorySystem():
    '''
        C_R_DF - датафрейм оцінок категорій ::колонки:: [category_id, user_id, rating] ::рядки:: кількість поставлених оцінок
        C_R - реальний датафрейм оцінок категорій ::колонки:: id категорій ::рядки:: id юзерів
        C_R_M - реальна матриця оцінок категорій
        C_P - датафрейм передбачення оцінки категорй з рейтингом більше 51% ::колонки:: [category_id, user_id, rating] ::рядки:: кількість передбачення оцінок
        C_U - профіль юзера в категоріях
        С - профіль категорії
        R_DF - датафрейм оцінок айтемів ::колонки:: [item_id, user_id, rating] ::рядки:: кількість поставлених оцінок
        R - реальний датафрейм оцінок айтемів ::колонки:: id айтемів ::рядки:: id юзерів
        R_M - реальна матриця оцінок айтемів
        U - профіль юзера
        I - профіль айтема
        P - датафрейм передбачень оцінок айтемів, які є в вподобаннях категорій ::колонки:: [category_id, user_id, rating] ::рядки:: id юзерів
        ItemData - датафрейт данних айтема ::колонки:: [item_id, category_id, item_mane, item_description] ::рядки:: кількість айтемів
        UserDate - датафрейт данних юзерів ::колонки:: [user_id, age, sex] ::рядки:: кількість юзерів
    '''

    def __init__(self):
        self.С_R_DF = None
        self.С_R = None
        self.C_R_M = None
        self.C_P = None
        self.С_U = None
        self.С = None
        self.R_DF = None
        self.R = None
        self.R_M = None
        self.U = None
        self.I = None
        self.P = None
        self.ItemData = None
        self.UserData = None
        self.CategoryData = None
        self.is_train = False

    def load_data(self):
        self.C_R_DF = pd.DataFrame(list(CategoryRating.objects.all().values_list('category_id', 'user_id', 'view')),
                                   columns=['category_id', 'user_id', 'rating'])
        self.R_DF = pd.DataFrame(list(BookRating.objects.all().values_list('book_id', 'user_id', 'view')),
                                 columns=['item_id', 'user_id', 'rating'])
        self.UserData = pd.DataFrame(list(User.objects.all().values_list('id')), columns=['user_id'])
        self.ItemData = pd.DataFrame(list(Book.objects.all().values_list('id', 'category_id', 'title', 'description')),
                                     columns=['item_id', 'category_id', 'item_mane', 'item_description'])
        self.CategoryData = pd.DataFrame(list(Categories.objects.all().values_list('id')), columns=['category_id', ])

        self.C_R = self.C_R_DF.pivot(
            index='user_id',
            columns='category_id',
            values='rating'
        )
        self.R = self.R_DF.pivot(
            index='user_id',
            columns='item_id',
            values='rating'
        )
        self.R_M = self.R.fillna(0).values
        self.C_R_M = self.C_R.fillna(0).values
        m, n = self.C_R_M.shape
        self.C_U = np.random.rand(10, m)
        self.C = np.random.rand(10, n)
        j, k = self.R_M.shape
        self.U = np.random.rand(10, j)
        self.I = np.random.rand(10, k)

    def predictions(self, U, I):
        return np.dot(U.T, I)

    def add_cold_users_and_items(self):
        cold_users = self.UserData[~self.UserData['user_id'].isin(self.R_DF.user_id.values)]
        cold_items = self.ItemData[~self.ItemData['item_id'].isin(self.R_DF.item_id.values)]
        cold_categories = self.CategoryData[~self.CategoryData['category_id'].isin(self.C_R_DF.category_id.values)]
        for user in cold_users.user_id.values:
            self.new_user(user, [4, 4, 4])
        for item in cold_items.item_id.values:
            self.new_item(item, {'category_id': self.ItemData[self.ItemData['item_id'] == item].category_id.values[0]})
        for category in cold_categories.category_id.values:
            self.new_category(category)

    def train(self):

        users, categories = self.C_R_M.nonzero()
        for epoch in range(20):
            for u, i in zip(users, categories):
                error = (self.C_R_M[u, i] - self.predictions(self.C_U[:, u], self.C[:, i]))
                self.C_U[:, u] += 0.1 * (error * self.C[:, i] - 0.5 * self.C_U[:, u])
                self.C[:, i] += 0.1 * (error * self.C_U[:, u] - 0.5 * self.C[:, i])

        users, items = self.R_M.nonzero()
        for epock in range(20):
            for u, i in zip(users, items):
                error = (self.R_M[u, i] - self.predictions(self.U[:, u], self.I[:, i]))
                self.U[:, u] += 0.1 * (error * self.I[:, i] - 0.5 * self.U[:, u])
                self.I[:, i] += 0.1 * (error * self.U[:, u] - 0.5 * self.I[:, i])

        self.C_P = pd.DataFrame(self.predictions(self.C_U, self.C), columns=self.C_R.columns,
                                index=self.C_R.index).stack().reset_index(name='rating')

        self.P = pd.DataFrame(self.predictions(self.U, self.I), columns=self.R.columns,
                              index=self.R.index).stack().reset_index(name='rating')

        P = self.P[self.P['item_id'].isin(
            self.ItemData[self.ItemData['category_id'].isin(self.C_P.category_id.values)].item_id.values)].values
        Reccomendation.objects.all().delete()
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])
        self.is_train = True

    def new_item(self, item_id, item_data):
        self.ItemData = self.ItemData.append(item_data, ignore_index=True)
        self.R[item_id] = np.nan
        self.R_M = np.pad(self.R_M, ((0, 0), (0, 1)), 'constant')
        ItemEmbending = np.random.rand(10, )
        self.I = np.pad(self.I, ((0, 0), (0, 1)), 'constant')
        self.I[:, -1] = ItemEmbending
        P = pd.DataFrame(self.predictions(self.U, ItemEmbending), columns=[item_id, ],
                         index=self.R.index)
        P.columns.name = 'item_id'
        P = P.stack().reset_index(name='rating')
        P = P[P['user_id'].isin(self.C_P[self.C_P['category_id'] == item_data['category_id']].user_id.values)].values
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])

    def new_user(self, user_id, user_data):
        self.UserData.append(user_data, ignore_index=True)
        self.R.loc[user_id] = np.nan
        self.C_R.loc[user_id] = np.nan
        self.R_M = np.pad(self.R_M, ((0, 1), (0, 0)), 'constant')
        self.C_R_M = np.pad(self.C_R_M, ((0, 1), (0, 0)), 'constant')
        CategoryUserEmbending = np.random.rand(10, ) / 5
        UserEmbending = np.random.rand(10, )

        self.U = np.pad(self.U, ((0, 0), (0, 1)), 'constant')
        self.U[:, -1] = UserEmbending
        self.C_U = np.pad(self.C_U, ((0, 0), (0, 1)), 'constant')
        self.C_U[:, -1] = CategoryUserEmbending

        new_category_predictions = pd.DataFrame(
            self.predictions(CategoryUserEmbending, self.C).reshape(1, self.C_R_M.shape[1]),
            columns=self.C_R.columns,
            index=[user_id, ])

        new_category_predictions.index.name = 'user_id'
        new_category_predictions = new_category_predictions.stack().reset_index(name='rating')

        self.C_P = self.C_P.append(new_category_predictions)
        P = pd.DataFrame(self.predictions(UserEmbending, self.I).reshape(1, self.R_M.shape[1]), columns=self.R.columns,
                         index=[user_id, ])
        P.index.name = 'user_id'
        P = P.stack().reset_index(name='rating')
        P = P[P['item_id'].isin(self.ItemData[self.ItemData['category_id'].isin(
            new_category_predictions.category_id.values)].item_id.values)].values

        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])

    def new_category(self, category_id):
        self.C_R[category_id] = np.nan
        self.C_R_M = np.pad(self.C_R_M, ((0, 0), (0, 1)), 'constant')
        self.C = np.pad(self.C, ((0, 0), (0, 1)), 'constant')

        CategoryEmbending = np.random.rand(10, )
        self.C[:, -1] = CategoryEmbending

        new_category_predictions = pd.DataFrame(self.predictions(self.C_U, CategoryEmbending),
                                                columns=[category_id],
                                                index=self.C_R.index)

        new_category_predictions.columns.name = 'category_id'
        new_category_predictions = new_category_predictions.stack().reset_index(name='rating')
        self.C_P = self.C_P.append(new_category_predictions)

    def change_rating(self, data):
        category_id = self.ItemData[self.ItemData['item_id'] == data['item_id']].category_id.values[0]
        self.C_R.loc[category_id, data['user_id']] = self.C_R.loc[category_id, data['user_id']] + 1
        self.R.loc[data['user_id'], data['item_id']] = self.R.loc[data['user_id'], data['item_id']] + 1

        user, item, category = np.where(self.R.index.to_numpy() == data['user_id'])[0][0], \
                               np.where(self.R.columns.to_numpy() == data['user_id'])[0][0], \
                               np.where(self.C_R.index.to_numpy() == category_id)[0][0]
        self.R_M[user, item] = self.R_M[user, item] + 1
        for epock in range(10):
            error = (self.C_R_M[user, category] - self.predictions(self.C_U[:, user], self.C[:, category]))
            self.C_U[:, user] += 0.1 * (error * self.C[:, category] - 0.5 * self.C_U[:, user])
            self.C[:, category] += 0.1 * (error * self.C_U[:, user] - 0.5 * self.C[:, item])

        for epock in range(10):
            error = (self.R_M[user, item] - self.predictions(self.U[:, user], self.I[:, item]))
            self.U[:, user] += 0.1 * (error * self.I[:, item] - 0.5 * self.U[:, user])
            self.I[:, item] += 0.1 * (error * self.U[:, user] - 0.5 * self.I[:, item])

        new_category_predictions = pd.DataFrame(
            self.predictions(self.C_U[:, user], self.C).reshape(1, self.C_R_M.shape[1]),
            columns=self.C_R.columns,
            index=[data['user_id'], ])
        f = self.C_R.stack().reset_index(name='rating')

        new_category_predictions.index.name = 'user_id'

        new_category_predictions = new_category_predictions.stack().reset_index(name='rating')

        P = pd.DataFrame(self.predictions(self.U[:, user], self.I).reshape(1, self.R_M.shape[1]),
                         columns=self.R.columns,
                         index=[data['user_id'], ])
        P.index.name = 'user_id'
        P = P.stack().reset_index(name='rating')
        P = P[P['item_id'].isin(self.ItemData[self.ItemData['category_id'].isin(
            new_category_predictions.category_id.values)].item_id.values)].values
        Reccomendation.objects.filter(user_id=data['user_id']).delete()
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])


class RecomendationItemSystem():
    def __init__(self):
        self.R_DF = None
        self.R = None
        self.R_M = None
        self.U = None
        self.I = None
        self.P = None
        self.ItemData = None
        self.UserData = None
        self.is_train = False

    def load_data(self):
        self.R_DF = pd.DataFrame(list(BookRating.objects.all().values_list('book_id', 'user_id', 'view')),
                                 columns=['item_id', 'user_id', 'rating'])
        self.UserData = pd.DataFrame(list(User.objects.all().values_list('id')), columns=['user_id'])
        self.ItemData = pd.DataFrame(list(Book.objects.all().values_list('id', 'category_id', 'title', 'description')),
                                     columns=['item_id', 'category_id', 'item_mane', 'item_description'])
        self.R = self.R_DF.pivot(
            index='user_id',
            columns='item_id',
            values='rating'
        )
        self.R_M = self.R.fillna(0).values
        j, k = self.R_M.shape
        self.U = np.random.rand(10, j)
        self.I = np.random.rand(10, k)

    def train(self):
        users, items = self.R_M.nonzero()
        for epock in range(20):
            for u, i in zip(users, items):
                error = (self.R_M[u, i] - self.predictions(self.U[:, u], self.I[:, i]))
                self.U[:, u] += 0.1 * (error * self.I[:, i] - 0.5 * self.U[:, u])
                self.I[:, i] += 0.1 * (error * self.U[:, u] - 0.5 * self.I[:, i])

        self.P = pd.DataFrame(self.predictions(self.U, self.I), columns=self.R.columns,
                              index=self.R.index).stack().reset_index(name='rating').values
        Reccomendation.objects.all().delete()
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])
        self.is_train = True

    def new_item(self, item_id, item_data):
        self.ItemData = self.ItemData.append(item_data, ignore_index=True)
        self.R[item_id] = np.nan
        self.R_M = np.pad(self.R_M, ((0, 0), (0, 1)), 'constant')
        ItemEmbending = np.random.rand(10, )
        self.I = np.pad(self.I, ((0, 0), (0, 1)), 'constant')
        self.I[:, -1] = ItemEmbending
        P = pd.DataFrame(self.predictions(self.U, ItemEmbending), columns=[item_id, ],
                         index=self.R.index)
        P.columns.name = 'item_id'
        P = P.stack().reset_index(name='rating').values
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])

    def new_user(self, user_id, user_data):
        self.UserData.append(user_data, ignore_index=True)
        self.R.loc[user_id] = np.nan
        self.R_M = np.pad(self.R_M, ((0, 1), (0, 0)), 'constant')
        UserEmbending = np.random.rand(10, )
        self.U = np.pad(self.U, ((0, 0), (0, 1)), 'constant')
        self.U[:, -1] = UserEmbending
        P = pd.DataFrame(self.predictions(UserEmbending, self.I).reshape(1, self.R_M.shape[1]),
                         columns=self.R.columns,
                         index=[user_id, ])
        P.index.name = 'user_id'
        P = P.stack().reset_index(name='rating').values
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                                            for m in P])

    def change_rating(self, data):
        self.R.loc[data['user_id'], data['item_id']] = self.R.loc[data['user_id'], data['item_id']] + 1
        user, item = np.where(self.R.index.to_numpy() == data['user_id'])[0][0], \
                               np.where(self.R.columns.to_numpy() == data['user_id'])[0][0], \
        self.R_M[user, item] = self.R_M[user, item] + 1
        for epock in range(10):
            error = (self.R_M[user, item] - self.predictions(self.U[:, user], self.I[:, item]))
            self.U[:, user] += 0.1 * (error * self.I[:, item] - 0.5 * self.U[:, user])
            self.I[:, item] += 0.1 * (error * self.U[:, user] - 0.5 * self.I[:, item])
        P = pd.DataFrame(self.predictions(self.U[:, user], self.I).reshape(1, self.R_M.shape[1]),
                         columns=self.R.columns,
                         index=[data['user_id'], ])
        P.index.name = 'user_id'
        P = P.stack().reset_index(name='rating').values
        Reccomendation.objects.filter(user_id=data['user_id']).delete()
        Reccomendation.objects.bulk_create([Reccomendation(**{'user_id': m[0],
                                                              'book_id': m[1],
                                                              'rating': m[2],
                                                              })
                                            for m in P])

R = RecomendationItemSystem()



def load_data():
    R.load_data()



def add_cold_users_and_items():
    R.add_cold_users_and_items()



def change_rating(data):
    R.change_rating(data)



def train():
    R.train()



def is_trained():
    return R.is_train



def new_user(user_id):
    R.new_user(user_id, [user_id, 5, 5])



def new_item(item_id):
    R.new_item(item_id, [item_id, 4, 4])


def new_category(category_id):
    R.new_category(category_id)
