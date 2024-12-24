from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..training.recommendation_model import RecommendationEngine
from ..models import UserRequest


class RecipeRecommendationView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the list of ingredients from the query parameters
        ingredients = request.GET.getlist("ingredients", [])

        if not ingredients:
            return Response(
                {"error": "No ingredients provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Initialize the recommendation engine
            recommender = RecommendationEngine()

            # Get the recommended recipes
            recommendations = recommender.recommend(ingredients)

            # Save the request to MongoDB
            user_request = UserRequest(
                ingredients=ingredients,
                recommendations=[rec["name"] for rec in recommendations]
            ).save()

            return Response(
                {
                    "request_id": str(user_request.id),
                    "recommendations": recommendations
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )