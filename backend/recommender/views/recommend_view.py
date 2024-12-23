from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..training.recommendation_model import RecommendationEngine


class RecipeRecommendationView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the list of ingredients from the query parameters
        ingredients = request.GET.getlist("ingredients")

        if not ingredients:
            return Response({"error": "No ingredients provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize the recommendation engine
        recommender = RecommendationEngine()

        # Get the recommended recipes based on the ingredients
        recommendations = recommender.recommend(ingredients)

        # Return the recommendations as a JSON response
        return Response(recommendations, status=status.HTTP_200_OK)
