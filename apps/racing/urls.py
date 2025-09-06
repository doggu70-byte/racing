from django.urls import path
from . import views

app_name = 'racing'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('prediction/', views.prediction_view, name='prediction'),
    path('api/test/', views.api_test, name='api_test'), 
    path('api/today-races/', views.today_races, name='today_races'),
    path('api/schedule/', views.api_schedule_data, name='api_schedule'),
    path('api/results/', views.api_race_results, name='api_results'),
    path('api/race-horses/', views.api_race_horses, name='api_race_horses'),
    path('api/horse-detail/', views.api_horse_detail, name='api_horse_detail'),
    path('api/prediction/', views.api_race_prediction, name='api_prediction'),
]