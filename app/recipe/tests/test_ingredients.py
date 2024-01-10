from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer
from decimal import Decimal

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_ur(ingredient_id):
    return reverse('recipes:ingredient-detail', args=[ingredient_id])

def create_user(email='user@example.com', password='pass555'):
    return get_user_model().objects.create_user(email=email, password=password)

class PublicIngredientApiTests(TestCase):
    def  setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientApiTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanila')
        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serilizer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serilizer.data)

    def tet_ingredients_limited_to_user(self):
        user2 = create_user(email='user2@example.com', password='pass333')
        Ingredient.objects.create(user=user2, name='Kale')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def tet_update_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')
        payload = {'name':'Coriander'}
        url = detail_ur(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(len(res.data), 1)
        self.assertEqual(ingredient.name, payload['name'])

    def tet_delete_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')
        url = detail_ur(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(len(res.data), 1)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        in1 = Ingredient.objects.create(user=self.user, name='Pepper')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Apple Crumb',
            time_minutes=5,
            price=Decimal('4.5'),
            )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only' : 1})
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        ing = Ingredient.objects.create(user=self.user, name='Pepper')
        Ingredient.objects.create(user=self.user, name='Turkey')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Apple Crumb',
            time_minutes=5,
            price=Decimal('4.5'),
            )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Herb eggs',
            time_minutes=3,
            price=Decimal('4.5'),
            )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only' : 1})
        self.assertEqual(len(res.data), 1)




