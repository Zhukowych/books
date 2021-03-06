from django.urls import path
from .views import *

app_name = "index"
urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('my_books/', MyBooks.as_view(), name='my_books'),
    path('add_book/', AddBook.as_view(), name="add_book"),
    path('book/<int:book_id>/', BookView.as_view(), name='book'),
    path('category/<int:category_id>', CategoryView.as_view(), name='category'),
    path('search/<str:title>/<str:author>/<int:category_id>/', SearchView.as_view(), name="search"),
    path('accounts_settings', AccountSettingsView.as_view(), name="account_settings"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path('change_user_data/', ChangeUserDataView.as_view(), name="change_user_data"),
    path('edit_book/<int:book_id>/', EditBook.as_view(), name='edit_book'),
    path('delete_book/<int:book_id>', DeleteBookView.as_view(), name='delete_book'),
    path('add_comment/<int:book_id>', AddCommentView.as_view(), name='add_comment'),
    path('admin_edit_book/<int:book_id>/', AdminEditBookView.as_view(), name='admin_edit_book'),
    path('messanges/', Messanges.as_view(), name="messanges"),
    path('send_ansver/<int:messange_id>', SendAnswerView.as_view(), name='send_answer'),
    path('admin_messanges/', AdminMessangesView.as_view(), name='admin_messanges'),
    path('accept_answer/<int:messange_id>/', AcceptAnswerView.as_view(), name='accept_answer'),
    path('not_accept_answer/<int:messange_id>/', NotAcceptAnswerView.as_view(), name='not_accept_answer'),
    path('delete_messange/<int:messange_id>/', DeleteMessangeView.as_view(), name='delete_messange'),
    path('favorite_books/', FavoriteBooks.as_view(), name="favorite_books"),
    path('change_favorite/<int:book_id>', ChangeFavoriteView.as_view(), name="change_favorite"),
    path('create_category/', CreateCategoryView.as_view(), name="create_category"),
    path('load_buffer/<int:state>/<int:book_id>/', LoadBufferBookView.as_view(), name='load_buffer'),
    path('delete_buffer/<str:name>/<int:state>/', DeleteBufferView.as_view(), name='delete_buffer')
]
