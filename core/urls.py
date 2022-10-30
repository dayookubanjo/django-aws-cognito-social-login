from .views import index,signout

from django.urls import path 

app_name = 'core'
urlpatterns = [
    path('', index, name='index'),   
    path('signout', signout, name='signout'),   
]