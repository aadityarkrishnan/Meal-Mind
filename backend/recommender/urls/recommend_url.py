from django.urls import path
from ..views.recommend_view import RecipeRecommendationView

urlpatterns = [
    path('recommend-recipes/', RecipeRecommendationView.as_view(), name='recommend-recipes'),
]
