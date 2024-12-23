import json
import re
from pathlib import Path
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from django.core.management.base import BaseCommand


class RecipeRecommender:
    def __init__(self, dataset_path, cleaned_data_path, model_path):
        self.dataset_path = dataset_path
        self.cleaned_data_path = cleaned_data_path
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer()
        self.cleaned_recipes = []

    def load_data(self):
        """Load raw dataset."""
        with open(self.dataset_path, "r") as f:
            self.recipes = json.load(f)

    def clean_ingredients(self, ingredients):
        """Clean and standardize ingredient names."""
        cleaned = []
        for ingredient in ingredients:
            ingredient = ingredient.lower()
            ingredient = re.sub(r"[^a-zA-Z\s]", "", ingredient)
            cleaned.append(ingredient.strip())
        return list(set(cleaned))

    def clean_data(self):
        """Clean the dataset."""
        self.cleaned_recipes = []
        for recipe in self.recipes:
            if "ingredients" in recipe and "name" in recipe:
                recipe["ingredients"] = self.clean_ingredients(recipe["ingredients"])
                self.cleaned_recipes.append(recipe)

        # Save cleaned data
        with open(self.cleaned_data_path, "w") as f:
            json.dump(self.cleaned_recipes, f)

    def train_model(self):
        """Train the TF-IDF model."""
        ingredient_lists = [" ".join(recipe["ingredients"]) for recipe in self.cleaned_recipes]
        ingredient_vectors = self.vectorizer.fit_transform(ingredient_lists)

        # Save the model
        with open(self.model_path, "wb") as f:
            pickle.dump((self.vectorizer, ingredient_vectors, self.cleaned_recipes), f)

    def execute(self):
        """Execute the entire cleaning and training pipeline."""
        self.load_data()
        self.clean_data()
        self.train_model()


class Command(BaseCommand):
    help = "Clean data and train the recommendation model"

    def handle(self, *args, **options):
        # Paths
        dataset_path = Path(settings.BASE_DIR) / "data" / "recipes.json"
        cleaned_data_path = Path(settings.BASE_DIR) / "data" / "cleaned_recipes.json"
        model_path = Path(settings.BASE_DIR) / "data" / "recommendation_model.pkl"

        # Run the pipeline
        recommender = RecipeRecommender(dataset_path, cleaned_data_path, model_path)
        recommender.execute()

        self.stdout.write(self.style.SUCCESS("Data cleaned and model trained successfully!"))
