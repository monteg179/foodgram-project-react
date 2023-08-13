import re
from typing import Any, Union
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import (
    exceptions,
    serializers,
    validators,
)
from rest_framework.authtoken.models import Token

from core.utils import base64_to_image
from recipes.models import (
    Favorite,
    Ingredient,
    Shopping,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class TokenSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: OrderedDict) -> OrderedDict:
        try:
            user = User.objects.get(email=data.get('email'))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed()
        if user.check_password(data.get('password')):
            data['user'] = user
        else:
            raise exceptions.AuthenticationFailed()
        return data

    def create(self, data) -> Token:
        return Token.objects.get_or_create(user=data['user'])[0]


class PasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value: str) -> str:
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError('Invalid value.')
        return value

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        user = self.context['user']
        user.set_password(data['new_password'])
        user.save()
        return data


class FoodgramUserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'password', 'is_subscribed')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_subscribed(self, user: User) -> bool:
        if hasattr(user, 'is_subscribed'):
            return user.is_subscribed
        return False


class TagColorField(serializers.Field):

    default_error_messages = {
        'invalid': 'Invalid format.',
    }

    FORMAT = r'^#(?:[0-9a-f]{3}){1,2}$'

    def to_representation(self, value: int) -> str:
        return f'#{value:06X}'

    def to_internal_value(self, value: str) -> int:
        if not re.match(type(self).FORMAT, value.lower()):
            self.fail('invalid')
        return int(value[1:], 16)


class TagSerializer(serializers.ModelSerializer):

    color = TagColorField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username', 'email', 'first_name',
                            'last_name')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('amount',)


class RecipeReadSerializer(serializers.ModelSerializer):

    author = RecipeAuthorSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredient',
        many=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_shopping'
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'image', 'cooking_time', 'author',
                  'tags', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = ('id', 'name', 'text', 'image', 'cooking_time')

    def get_favorited(self, recipe: Recipe) -> bool:
        if hasattr(recipe, 'is_favorited'):
            return recipe.is_favorited
        return False

    def get_shopping(self, recipe: Recipe) -> bool:
        if hasattr(recipe, 'is_in_shopping_cart'):
            return recipe.is_in_shopping_cart
        return False


class RecipeImageField(serializers.ImageField):

    def to_internal_value(
            self, data: Union[str, Any]) -> Union[ContentFile, Any]:
        if isinstance(data, str) and data.startswith('data:image'):
            return base64_to_image(data)
        return super().to_internal_value(data)


class RecipeIngredientWriteSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate_id(self, value: int) -> Ingredient:
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Ingredient not exist')
        return value

    def validate_amount(self, value: int) -> int:
        if (value < 1):
            serializers.ValidationError('Incorrect value')
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):

    image = RecipeImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'image', 'cooking_time', 'tags',
                  'ingredients')
        read_only_fields = ('id',)

    def create(self, data: dict[str, Any]) -> Recipe:
        tags_data = data.pop('tags')
        ingredients_data = data.pop('ingredients')
        recipe = Recipe.objects.create(**data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe.id, ingredients_data)
        return recipe

    def update(self, recipe: Recipe, data: dict[str, Any]) -> Recipe:
        recipe.name = data.get('name', recipe.name)
        recipe.text = data.get('text', recipe.text)
        recipe.image = data.get('image', recipe.image)
        recipe.cooking_time = data.get('cooking_time', recipe.cooking_time)
        tags_data = data.get('tags')
        if tags_data:
            recipe.tags.set(tags_data)
        ingredients_data = data.get('ingredients')
        if ingredients_data:
            recipe.ingredients.delete()
            self.create_ingredients(recipe.id, data)
        recipe.save()
        return recipe

    def create_ingredients(self, recipe_id: int, data: list[OrderedDict]):
        ingrediets = [
            RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=item['id'],
                amount=item['amount']
            )
            for item in data
        ]
        RecipeIngredient.objects.bulk_create(ingrediets)

    def to_representation(self, recipe: Recipe) -> OrderedDict:
        return RecipeReadSerializer(recipe).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def to_representation(self, favorite: Favorite) -> OrderedDict:
        return RecipeMinifiedSerializer(instance=favorite.recipe).data


class ShoppingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shopping
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Shopping.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def to_representation(self, shopping: Shopping) -> OrderedDict:
        return RecipeMinifiedSerializer(instance=shopping.recipe).data


class SubscriptionReadSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
    )
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'recipes', 'recipes_count', 'is_subscribed')

    def get_recipes_count(self, subscription: Subscription) -> int:
        return subscription.author.recipes.count()

    def get_recipes(self, subscription: Subscription):
        recipes_limit = self.context.get('recipes_limit')
        recipes = subscription.author.recipes.all()[:recipes_limit]
        result = [
            RecipeMinifiedSerializer(instance=recipe).data
            for recipe in recipes
        ]
        return result

    def get_subscribed(self, subscription: Subscription) -> bool:
        if hasattr(subscription, 'is_subscribed'):
            return subscription.is_subscribed
        return True


class SubscriptionWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
            )
        ]

    def to_representation(self, subscription: Subscription) -> OrderedDict:
        return SubscriptionReadSerializer(
            instance=subscription,
            context=self.context
        ).data
