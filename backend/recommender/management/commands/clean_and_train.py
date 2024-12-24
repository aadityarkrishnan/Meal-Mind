# recommender/management/commands/clean_and_train.py
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
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            min_df=1,
            token_pattern=r'(?u)\b\w+\b'
        )
        self.cleaned_recipes = []

    def load_data(self):
        """Load raw dataset."""
        try:
            with open(self.dataset_path, "r", encoding='utf-8') as f:
                self.recipes = json.load(f)
            print(f"Loaded {len(self.recipes)} recipes")
        except FileNotFoundError:
            raise Exception(f"Dataset not found at {self.dataset_path}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON format in dataset")

    def clean_ingredient(self, ingredient):
        """Clean a single ingredient string."""
        if not ingredient:  # Check if ingredient is None or empty
            return None

        try:
            # Convert to string in case we get a non-string input
            ingredient = str(ingredient)

            # Clean the ingredient
            ingredient = ingredient.encode('ascii', 'ignore').decode()
            ingredient = ingredient.lower()
            ingredient = re.sub(r'\d+(/\d+)?', '', ingredient)
            ingredient = re.sub(r'\([^)]*\)', '', ingredient)
            ingredient = re.sub(r'[^\w\s]', ' ', ingredient)
            ingredient = ' '.join(ingredient.split())

            # Return None if we're left with an empty string
            cleaned = ingredient.strip()
            return cleaned if cleaned else None

        except Exception:
            return None

    def clean_data(self):
        """Clean the dataset."""
        self.cleaned_recipes = []
        skipped_recipes = 0

        for recipe in self.recipes:
            try:
                # Get title from basic_info with safety checks
                basic_info = recipe.get("basic_info", {}) or {}
                name = (basic_info.get("title") or "Unknown Recipe").strip()

                # Get prep data with safety checks
                prep_data = recipe.get("prep_data", {}) or {}

                # Safe string processing function
                def safe_clean_string(value):
                    if value is None:
                        return ""
                    return str(value).replace(":", "").strip()

                # Handle ingredients
                ingredients = recipe.get("ingridients", []) or []

                if ingredients:
                    cleaned_ingredients = []
                    for ingredient in ingredients:
                        cleaned = self.clean_ingredient(ingredient)
                        if cleaned is not None and cleaned != "":
                            cleaned_ingredients.append(cleaned)

                    if cleaned_ingredients:
                        # Safely get all values
                        cleaned_recipe = {
                            "name": name,
                            "ingredients": cleaned_ingredients,
                            "prep_time": safe_clean_string(prep_data.get("prep_time:")),
                            "cook_time": safe_clean_string(prep_data.get("cook_time:")),
                            "additional_time": safe_clean_string(prep_data.get("additional_time:")),
                            "total_time": safe_clean_string(prep_data.get("total_time:")),
                            "servings": safe_clean_string(prep_data.get("servings:")),
                            "yield": safe_clean_string(prep_data.get("yield:")),
                            "nutritions": recipe.get("nutritions", {}),
                            "category": basic_info.get("category", ""),
                            "rating": safe_clean_string(basic_info.get("rating")),
                            "rating_count": safe_clean_string(basic_info.get("rating_count")),
                            "state": recipe.get("state", "")
                        }
                        self.cleaned_recipes.append(cleaned_recipe)
                    else:
                        skipped_recipes += 1
                else:
                    skipped_recipes += 1

            except Exception as e:
                print(f"Error processing recipe: {str(e)}")
                skipped_recipes += 1
                continue

        print(f"Cleaned {len(self.cleaned_recipes)} recipes")
        print(f"Skipped {skipped_recipes} recipes with no valid ingredients")

        # Save cleaned data
        with open(self.cleaned_data_path, "w", encoding='utf-8') as f:
            json.dump(self.cleaned_recipes, f, ensure_ascii=False, indent=2)

        # Save cleaned data
        with open(self.cleaned_data_path, "w", encoding='utf-8') as f:
            json.dump(self.cleaned_recipes, f, ensure_ascii=False, indent=2)

    def train_model(self):
        """Train the TF-IDF model."""
        if not self.cleaned_recipes:
            raise Exception("No cleaned recipes available for training")

        ingredient_lists = [" ".join(recipe["ingredients"]) for recipe in self.cleaned_recipes]

        if not any(ingredient_lists):
            raise Exception("No valid ingredients found for training")

        print(f"Training on {len(ingredient_lists)} recipes")

        ingredient_vectors = self.vectorizer.fit_transform(ingredient_lists)

        print(f"Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        print(f"Feature matrix shape: {ingredient_vectors.shape}")

        with open(self.model_path, "wb") as f:
            pickle.dump((self.vectorizer, ingredient_vectors, self.cleaned_recipes), f)

    def execute(self):
        """Execute the entire cleaning and training pipeline."""
        print("Starting recipe recommendation model training...")
        self.load_data()
        self.clean_data()
        self.train_model()
        print("Training completed successfully!")


class Command(BaseCommand):
    help = "Clean recipe data and train the recommendation model"

    def handle(self, *args, **options):
        try:
            dataset_path = Path(settings.BASE_DIR) / "data" / "recipes.json"
            cleaned_data_path = Path(settings.BASE_DIR) / "data" / "cleaned_recipes.json"
            model_path = Path(settings.BASE_DIR) / "data" / "recommendation_model.pkl"

            recommender = RecipeRecommender(dataset_path, cleaned_data_path, model_path)
            recommender.execute()

            self.stdout.write(
                self.style.SUCCESS("Data cleaned and model trained successfully!")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error: {str(e)}")
            )