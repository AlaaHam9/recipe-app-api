from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id','name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id','name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id','title','time_minutes','price','link','tags','ingredients']
        read_only_fields = ['id'] # by default nested serializer is readonly

    # helper function
    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
           tag_obj, created =Tag.objects.get_or_create(user=auth_user, **tag)  # get_or_create create if not exists
           recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context['request'].user
        for ingredient in ingredients:
           ingredient_obj, created =Ingredient.objects.get_or_create(user=auth_user, **ingredient)
           recipe.ingredients.add(ingredient_obj)


    # override the create method to add ability to add tags in the creation, because rest framework not support the neasted serializer
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags,instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients,instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description','image']

# we add seperate serialaizer for  image because when we upload images we only need to accepts the image field
class RecipeImageSerializer(serializers.ModelSerializer):
    """Serialiazer for uploading images to recipes."""
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}