import pickle
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from django.conf import settings


class RecommendationEngine:
    def __init__(self):
        try:
            model_path = Path(settings.BASE_DIR) / "data" / "recommendation_model.pkl"
            if not model_path.exists():
                raise FileNotFoundError(
                    "Model file not found. Please run 'python manage.py clean_and_train' first."
                )

            with open(model_path, "rb") as f:
                self.vectorizer, self.ingredient_vectors, self.cleaned_recipes = pickle.load(f)
        except Exception as e:
            raise Exception(f"Failed to load recommendation model: {str(e)}")

    def clean_ingredients(self, ingredients):
        """Clean input ingredients using the same process as training."""
        cleaned = []
        for ingredient in ingredients:
            # Convert to lowercase and strip whitespace
            ingredient = ingredient.lower().strip()
            if ingredient:
                cleaned.append(ingredient)
        return cleaned

    def recommend(self, input_ingredients, top_n=5):
        """Recommend recipes based on input ingredients."""
        try:
            cleaned_ingredients = self.clean_ingredients(input_ingredients)
            if not cleaned_ingredients:
                raise ValueError("No valid ingredients after cleaning")

            input_text = " ".join(cleaned_ingredients)
            input_vector = self.vectorizer.transform([input_text])
            similarity_scores = cosine_similarity(input_vector, self.ingredient_vectors)[0]

            # Create recipe entries with scores
            recipe_scores = [
                {
                    "name": recipe.get("name", "Unknown Recipe"),
                    "ingredients": recipe.get("ingredients", []),
                    "similarity_score": float(score),
                    "nutritions": recipe.get("nutritions", {}),
                    "prep_time": recipe.get("prep_time", ""),
                    "additional_time": recipe.get("additional_time", ""),
                    "total_time": recipe.get("total_time", ""),
                    "servings": recipe.get("servings", ""),
                    "yield": recipe.get("yield", ""),
                    "category": recipe.get("category", ""),
                    "rating": recipe.get("rating", ""),
                    "rating_count": recipe.get("rating_count", ""),
                    "state": recipe.get("state", "")
                }
                for recipe, score in zip(self.cleaned_recipes, similarity_scores)
                if float(score) > 0.1  # Filter out very low similarity scores
            ]

            # Sort by similarity score and get top N
            recommendations = sorted(
                recipe_scores,
                key=lambda x: x["similarity_score"],
                reverse=True
            )[:top_n]

            return recommendations

        except Exception as e:
            raise Exception(f"Recipe recommendation failed: {str(e)}")