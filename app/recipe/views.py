from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer
)
from core.models import Recipe, Tag, Ingredient
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

# Add filtering to the API docs manually, extend the auto generating schema by django rest spectacular
@extend_schema_view(
    list=extend_schema(  # for the list endpoint
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma sperated list of tags IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma sperated list of ingredients IDs to filter'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_inst(self, qs):
        """Helper function used in filtering the reipes , it convert list of strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    # override the default method to get the recipes for the auth user only
    def get_queryset(self):
        """Retrieve recipes for auth user."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_inst(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_inst(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    # override it because we want use te detail serialaizer instead of the default one for the list view
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'upload_image':   # This is a custom action, we must define it
            return RecipeImageSerializer
        return self.serializer_class

    # override default to save the auth user in creation
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Define the upload_image action
    @action(methods=['POST'], detail=True, url_path='upload-image')  # detail=True specific id of a recipe (not list)
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add filtering to the API docs manually, extend the auto generating schema by django rest spectacular
@extend_schema_view(
    list=extend_schema(  # for the list endpoint
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0,1],
                description='Filter by items assigned to recipes.'
            ),
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin, 
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes  = [TokenAuthentication]
    permission_classes      = [IsAuthenticated]

    # override it to get the tags for the auth user just
    def get_queryset(self):
        """Filter queryset to authenticate user."""
        assigned_only = bool (int (self.request.query_params.get('assigned_only',0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name').distinct()



class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class        = TagSerializer
    queryset                = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class        = IngredientSerializer
    queryset                = Ingredient.objects.all()
