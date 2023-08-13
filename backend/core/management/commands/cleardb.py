from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Shopping,
    Tag,
)
from users.models import (
    FoodgramUser,
    Subscription,
)


class Command(BaseCommand):

    help = 'Clear database'

    def handle(self, *args, **kwargs) -> None:
        try:
            print('clear FoodgramUser')
            FoodgramUser.clear_data()
            print('clear Subscription')
            Subscription.clear_data()
            print('clear Recipe')
            Recipe.clear_data()
            print('clear Tag')
            Tag.clear_data()
            print('clear Ingredient')
            Ingredient.clear_data()
            print('clear RecipeIngredient')
            RecipeIngredient.clear_data()
            print('clear RecipeTag')
            RecipeTag.clear_data()
            print('clear Favorite')
            Favorite.clear_data()
            print('clear Shopping')
            Shopping.clear_data()
        except Exception as error:
            raise CommandError(f'error:{type(error)} = {error}')
