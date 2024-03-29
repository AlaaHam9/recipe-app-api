from django.urls import path, include
from recipe import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# RecipeViewSet auto generates urls depending on the functionality that's enabled on the view set
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name='recipe'

urlpatterns = [
    path('', include(router.urls))
]
