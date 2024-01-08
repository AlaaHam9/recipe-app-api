from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # override the default method to get the recipes for the auth user only
    def get_queryset(self):
        """Retrieve recipes for auth user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # override it because we want use te detail serialaizer instead of the default one for the list view
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class

    # override default to save the auth user in creation
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)