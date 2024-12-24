from django.urls import path
from recommender.views.recommend_view import RecipeRecommendationView

urlpatterns = [
    path('recommend/', RecipeRecommendationView.as_view(), name='recommend-recipes'),
]
