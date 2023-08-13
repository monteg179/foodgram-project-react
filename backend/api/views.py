import csv
from typing import Any, Iterable, Mapping, Union

from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Value, Sum
from django.db.models.query import QuerySet
from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as django_filter
from rest_framework import (
    exceptions,
    filters,
    pagination,
    permissions,
    status,
    views,
)
from rest_framework.request import Request
from rest_framework.response import Response
from api.filters import RecipeFilter
from api.serializers import (
    FavoriteSerializer,
    FoodgramUserSerializer,
    IngredientSerializer,
    PasswordSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingSerializer,
    SubscriptionReadSerializer,
    SubscriptionWriteSerializer,
    TagSerializer,
    TokenSerializer
)

from api.permissions import AuthorOrReadOnly
from core.utils import str_to_int

from recipes.models import (
    Favorite,
    Ingredient,
    Shopping,
    Recipe,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class FoodgramView(views.APIView):

    def get_permissions(self):
        if getattr(type(self), 'safety', None):
            value = type(self).safety
            if isinstance(value, Mapping):
                value = value.get(self.request.method)
            if not isinstance(value, Iterable):
                value = (value,)
            type(self).permission_classes = value
        return super().get_permissions()

    def handle_exception(self, error: Exception) -> Response:
        if isinstance(error, exceptions.ValidationError):
            error_data = {'errors': str(error)}
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(error)


class FoodgramModelView(FoodgramView):

    def get_queryset(self) -> QuerySet:
        raise NotImplementedError()

    def get_object(self):
        return get_object_or_404(self.filter_queryset(), id=self.kwargs['pk'])

    def filter_queryset(self) -> QuerySet:
        queryset = self.get_queryset()
        if not hasattr(self, 'filter_backends') or not self.filter_backends:
            return queryset
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class FoodgramPaginator(pagination.PageNumberPagination):

    page_size_query_param = 'limit'
    page_size = 10


class TokenCreateView(FoodgramView):
    """ api/auth/token/login """

    safety = permissions.AllowAny

    def post(self, request: Request) -> Response:
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response(
            data={'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )


class TokenDestroyView(FoodgramView):
    """ api/auth/token/logout """

    safety = permissions.IsAuthenticated

    def post(self, request: Request) -> Response:
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        if user.is_authenticated:
            subquery = Subscription.objects.filter(
                user=user,
                author_id=OuterRef('id')
            )
            return User.objects.annotate(is_subscribed=Exists(subquery))
        return User.objects.annotate(is_subscribed=Value(False))


class UserListView(UserBaseView):
    """ api/users/ """

    safety = {
        'GET': permissions.IsAdminUser,
        'POST': permissions.AllowAny,
    }

    def get(self, request: Request) -> Response:
        paginator = FoodgramPaginator()
        queryset = paginator.paginate_queryset(
            queryset=self.filter_queryset(),
            request=self.request
        )
        serializer = FoodgramUserSerializer(instance=queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = FoodgramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(UserBaseView):
    """ api/users/<int:pk>/ """

    safety = permissions.IsAuthenticated

    def get(self, request: Request, pk: int) -> Response:
        user = self.get_object()
        serializer = FoodgramUserSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserMeView(UserBaseView):
    """ api/users/me/ """

    safety = permissions.IsAuthenticated

    def get(self, request: Request) -> Response:
        user = get_object_or_404(self.get_queryset(), id=request.user.id)
        serializer = FoodgramUserSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserPasswordView(FoodgramView):
    """ api/users/set_setpassword """

    safety = permissions.IsAuthenticated

    def post(self, request: Request) -> Response:
        context = {
            'user': request.user
        }
        serializer = PasswordSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SubscriptionBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        subquery = User.objects.filter(id=OuterRef('user_id'))
        return Subscription.objects.filter(user=user).annotate(
            is_subscribed=Exists(subquery)
        )

    def get_object(self) -> Union[Subscription, None]:
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs['pk'])
        try:
            return Subscription.objects.get(user=user, author=author)
        except Subscription.DoesNotExist:
            raise exceptions.ValidationError('Subscription not exist')

    def get_recipes_limit(self, data: QueryDict) -> Union[int, None]:
        return str_to_int(data.get('recipes_limit'))


class SubscribtionView(SubscriptionBaseView):
    """ api/users/subscription/ """

    safety = permissions.IsAuthenticated

    def get(self, request: Request) -> Response:
        context = {
            'recipes_limit': self.get_recipes_limit(request.query_params)
        }
        paginator = FoodgramPaginator()
        queryset = paginator.paginate_queryset(
            queryset=self.filter_queryset(),
            request=self.request
        )
        serializer = SubscriptionReadSerializer(
            instance=queryset,
            context=context,
            many=True
        )
        return paginator.get_paginated_response(serializer.data)


class SubscribeView(SubscriptionBaseView):
    """ api/users/<int:pk>/subscribe/ """

    safety = permissions.IsAuthenticated

    def post(self, request: Request, pk: int) -> Response:
        author = get_object_or_404(User, id=pk)
        data = {
            'user': request.user.id,
            'author': author.id
        }
        context = {
            'recipes_limit': self.get_recipes_limit(request.query_params)
        }
        serializer = SubscriptionWriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk: int) -> Response:
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        return Tag.objects.all()


class TagListView(TagBaseView):
    """ api/tags/ """

    safety = permissions.AllowAny

    def get(self, request: Request) -> Response:
        queryset = self.filter_queryset()
        serializer = TagSerializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TagDetailView(TagBaseView):
    """ api/tags/<int:pk>/ """

    safety = permissions.AllowAny

    def get(self, request: Request, pk: int) -> Response:
        tag = self.get_object()
        serializer = TagSerializer(instance=tag)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class IngredientBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        return Ingredient.objects.all()


class IngredientListView(IngredientBaseView):
    """ api/ingredients/ """

    safety = permissions.AllowAny

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get(self, request: Request) -> Response:
        queryset = self.filter_queryset()
        serializer = IngredientSerializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class IngredientDetailView(IngredientBaseView):
    """ api/ingredients/<int:pk>/ """

    safety = permissions.AllowAny

    def get(self, request: Request, pk: int) -> Response:
        ingredient = self.get_object()
        serializer = IngredientSerializer(instance=ingredient)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RecipeBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        if user.is_authenticated:
            favorite = Favorite.objects.filter(
                user=user,
                recipe_id=OuterRef('id')
            )
            shopping = Shopping.objects.filter(
                user=user,
                recipe_id=OuterRef('id')
            )
            return Recipe.objects.annotate(
                is_favorited=Exists(favorite),
                is_in_shopping_cart=Exists(shopping)
            )
        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
        )


class RecipeListView(RecipeBaseView):
    """ api/recipes/ """

    safety = permissions.IsAuthenticatedOrReadOnly

    filter_backends = (django_filter.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get(self, request: Request) -> Response:
        paginator = FoodgramPaginator()
        queryset = paginator.paginate_queryset(
            queryset=self.filter_queryset(),
            request=self.request
        )
        serializer = RecipeReadSerializer(instance=queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = RecipeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeDetailView(RecipeBaseView):
    """ api/recipes/<int:pk>/ """

    safety = AuthorOrReadOnly

    def get(self, request: Request, pk: int) -> Response:
        recipe = self.get_object()
        serializer = RecipeReadSerializer(instance=recipe)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, pk: int) -> Response:
        return self.update(request.data)

    def patch(self, request: Request, pk: int) -> Response:
        return self.update(request.data, True)

    def delete(self, request: Request, pk: int) -> Response:
        recipe = self.get_object()
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, data: dict[str, Any], partial: bool = False) -> Response:
        serializer = RecipeWriteSerializer(
            instance=self.get_object(),
            data=data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class FavoriteBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        return Favorite.objects.all()

    def get_object(self) -> Favorite:
        user = self.request.user
        try:
            recipe = Recipe.objects.get(id=self.kwargs['pk'])
            favorite = Favorite.objects.get(user=user, recipe=recipe)
        except Recipe.DoesNotExist:
            raise exceptions.ValidationError('Recipe not exist')
        except Favorite.DoesNotExist:
            raise exceptions.ValidationError('Favorite not exist')
        else:
            return favorite


class FavoriteView(FavoriteBaseView):
    """ api/recipes/<int:pk>/favorite/ """

    safety = permissions.IsAuthenticated

    def post(self, request: Request, pk: int) -> Response:
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk: int) -> Response:
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingBaseView(FoodgramModelView):

    def get_queryset(self) -> QuerySet:
        return Shopping.objects.all()

    def get_object(self) -> Shopping:
        user = self.request.user
        try:
            recipe = Recipe.objects.get(id=self.kwargs['pk'])
            shopping = Shopping.objects.get(user=user, recipe=recipe)
        except Recipe.DoesNotExist:
            raise exceptions.ValidationError('Recipe not exist')
        except Shopping.DoesNotExist:
            raise exceptions.ValidationError('Shopping not exist')
        else:
            return shopping


class ShoppingView(ShoppingBaseView):
    """ api/recipes/<int:pk>/shopping_cart/ """

    safety = permissions.IsAuthenticated

    def post(self, request: Request, pk: int) -> Response:
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = ShoppingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk: int) -> Response:
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartBaseView(FoodgramModelView):

    FIELD_NAMES = ('name', 'measurement_unit', 'total')

    def get_queryset(self) -> QuerySet:
        return Ingredient.objects.filter(
            recipe_ingredient__recipe__shopping_recipe__user=self.request.user
        ).annotate(
            total=Sum('recipe_ingredient__amount')
        ).values_list(
            *type(self).FIELD_NAMES
        )


class DownloadShoppingCartView(DownloadShoppingCartBaseView):

    safety = permissions.IsAuthenticated

    FILE_NAME = 'shopping_cart.csv'

    def get(self, request: Request) -> HttpResponse:
        queryset = self.get_queryset()
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename='
                                       f'"{type(self).FILE_NAME}"'
            }
        )
        writer = csv.writer(response)
        writer.writerow(type(self).FIELD_NAMES)
        writer.writerows(queryset)
        return response
