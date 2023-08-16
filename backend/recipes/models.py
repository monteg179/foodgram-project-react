from typing import Any, Final

from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from core.models import FoodgramModelMixin
from core.utils import (
    base64_to_image,
    image_to_base64,
)

User = get_user_model()


class Tag(models.Model, FoodgramModelMixin):

    NAME_MAX_LENGTH: Final[int] = 200
    MAX_COLOR: Final[int] = 0xFFFFFF

    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    color = models.PositiveIntegerField(
        verbose_name='Цвет',
        validators=(
            MaxValueValidator(MAX_COLOR),
        ),
        unique=True,
    )

    slug = models.SlugField(
        verbose_name='Уникальный слаг',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'Tag':
        return cls.objects.create(**data)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'name', 'color', 'slug')

    @classmethod
    def export_data(cls, instance: 'Tag') -> dict[str, Any]:
        return {
            'id': instance.id,
            'name': instance.name,
            'color': instance.color,
            'slug': instance.slug,
        }


class Ingredient(models.Model, FoodgramModelMixin):

    NAME_MAX_LENGTH: Final[int] = 200
    MEASUREMENT_UNIT_MAX_LENGTH: Final[int] = 200

    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
        db_index=True,
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'Ingredient':
        return cls.objects.create(**data)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'name', 'measurement_unit')

    @classmethod
    def export_data(cls, instance: 'Ingredient') -> dict[str, Any]:
        return {
            'id': instance.id,
            'name': instance.name,
            'measurement_unit': instance.measurement_unit,
        }


class Recipe(models.Model, FoodgramModelMixin):

    NAME_MAX_LENGTH: Final[int] = 200
    MIN_COOCKING_TIME: Final[int] = 1
    MAX_COOCKING_TIME: Final[int] = 32_000

    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
    )

    text = models.TextField(
        verbose_name='Описание',
        blank=False,
        null=False
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe/images/',
        blank=False,
        null=False
    )

    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(
            MinValueValidator(MIN_COOCKING_TIME),
            MaxValueValidator(MAX_COOCKING_TIME),
        )
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    tags = models.ManyToManyField(
        verbose_name='Тэги рецепта',
        to=Tag,
        through='RecipeTag'
    )

    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты рецептов',
        to=Ingredient,
        through='RecipeIngredient',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'Recipe':
        instance = cls.objects.create(
            id=data.get('id'),
            name=data.get('name'),
            text=data.get('text'),
            image=base64_to_image(data.get('image')),
            cooking_time=data.get('cooking_time'),
            author_id=data.get('author_id')
        )
        return instance

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'name', 'text', 'image', 'cooking_time', 'author_id')

    @classmethod
    def export_data(cls, instance: 'Recipe') -> dict[str, Any]:
        return {
            'id': instance.id,
            'name': instance.name,
            'text': instance.text,
            'image': image_to_base64(instance.image.path),
            'cooking_time': instance.cooking_time,
            'author_id': instance.author_id,
        }


class RecipeTag(models.Model, FoodgramModelMixin):

    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )

    tag = models.ForeignKey(
        verbose_name='Тэг',
        to=Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэти рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag',
            ),
        ]
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.recipe} <-> {self.tag}'

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'RecipeTag':
        return cls.objects.create(**data)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'recipe_id', 'tag_id')

    @classmethod
    def export_data(cls, instance: 'RecipeTag') -> dict[str, Any]:
        return {
            'id': instance.id,
            'recipe_id': instance.recipe_id,
            'tag_id': instance.tag_id,
        }


class RecipeIngredient(models.Model, FoodgramModelMixin):

    MIN_AMOUNT: Final[int] = 1
    MAX_AMOUNT: Final[int] = 32_000

    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )

    ingredient = models.ForeignKey(
        verbose_name='Ингредиент',
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )

    amount = models.IntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.recipe} <-> {self.ingredient}'

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'RecipeIngredient':
        return cls.objects.create(**data)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'recipe_id', 'ingredient_id', 'amount')

    @classmethod
    def export_data(cls, instance: 'RecipeIngredient') -> dict[str, Any]:
        return {
            'id': instance.id,
            'recipe_id': instance.recipe_id,
            'ingredient_id': instance.ingredient_id,
            'amount': instance.amount
        }


class UserRecipe(models.Model, FoodgramModelMixin):

    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user'
    )

    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} <-> {self.recipe}'

    def favorites_amount(self) -> int:
        return self.favorite_recipe.count()

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'UserRecipe':
        return cls.objects.create(**data)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'user_id', 'recipe_id')

    @classmethod
    def export_data(cls, instance: 'UserRecipe') -> dict[str, Any]:
        return {
            'id': instance.id,
            'user_id': instance.user_id,
            'recipe_id': instance.recipe_id
        }


class Favorite(UserRecipe):

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('id',)


class Shopping(UserRecipe):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('id',)
