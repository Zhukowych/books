"""books URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from index.models import *
from django.http import Http404
from graphene_django.views import GraphQLView

def protected_serve(request, path, document_root=None, show_indexes=False):
    if "books" in path:
        bookfile = BookFiles.objects.get(file=path)

        book = bookfile.book

        if book.is_public:
            return serve(request, path, document_root, show_indexes)
        elif request.user.is_authenticated and not book.is_public and book.upload_author == request.user:
            return serve(request, path, document_root, show_indexes)
        elif not request.user.is_authenticated and book.is_public:
            return serve(request, path, document_root, show_indexes)
        else:
            raise Http404("В вас не має прав на данну книгу")
    else:
        return serve(request, path, document_root, show_indexes)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("index.urls")),
    path('graphql', GraphQLView.as_view(graphiql=True)),
]

urlpatterns += static(settings.MEDIA_URL, protected_serve, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, protected_serve, document_root=settings.MEDIA_ROOT)
