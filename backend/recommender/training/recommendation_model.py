import pickle
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from django.conf import settings


class RecommendationEngine:
    def __init__(self):
        model_path = Path(settings.BASE_DIR) / "data" / "recommendation_model.pkl"
        with open(model_path, "rb") as f:
            self.vectorizer, self.ingredient_vectors, self.cleaned_recipes = pickle.load(f)

    def recommend(self, input_ingredients, top_n=5):
        """Recommend recipes based on input ingredients."""
        input_text = " ".join(input_ingredients)
        input_vector = self.vectorizer.transform([input_text])

        # Calculate similarity
        similarity_scores = cosine_similarity(input_vector, self.ingredient_vectors)
        top_indices = similarity_scores[0].argsort()[-top_n:][::-1]

        # Fetch top recipes
        recommendations = []
        for index in top_indices:
            recommendations.append({
                "name": self.cleaned_recipes[index]["name"],
                "ingredients": self.cleaned_recipes[index]["ingredients"],
            })
        return recommendations
