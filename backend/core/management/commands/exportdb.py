from django.core.management.base import (
    BaseCommand,
    CommandError,
)

import core.models
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
    Subscription
)


class Command(BaseCommand):

    help = 'Export database from files'

    USER_FILE = 'users'
    SUBSCRIPTION_FILE = 'subscribtions'
    TAG_FILE = 'tags'
    INGREDIENT_FILE = 'ingredients'
    RECIPE_FILE = 'recipes'
    RECIPE_TAG_FILE = 'recipe_tags'
    RECIPE_INGREDIENT_FILE = 'recipe_ingredients'
    FAVORITE_FILE = 'favorites'
    SHOPPING_FILE = 'shopping'

    EXT = {
        core.models.CSV_FORMAT: '.csv',
        core.models.JSON_FORMAT: '.json',
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--format',
            choices=core.models.FORMAT_ENUM,
            help='Files format.'
        )
        parser.add_argument(
            '-p', '--path',
            type=str,
            help='Folder path.'
        )

    def handle(self, *args, **kwargs) -> None:
        format = kwargs['format']
        path = kwargs['path']
        cls = type(self)
        try:
            file_name = f'{path}/{cls.USER_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            FoodgramUser.save_to_file(file_name, format)
            file_name = f'{path}/{cls.SUBSCRIPTION_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            Subscription.save_to_file(file_name, format)
            file_name = f'{path}/{cls.TAG_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            Tag.save_to_file(file_name, format)
            file_name = f'{path}/{cls.INGREDIENT_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            Ingredient.save_to_file(file_name, format)
            file_name = f'{path}/{cls.RECIPE_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            Recipe.save_to_file(file_name, format)
            file_name = f'{path}/{cls.RECIPE_TAG_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            RecipeTag.save_to_file(file_name, format)
            file_name = f'{path}/{cls.RECIPE_INGREDIENT_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            RecipeIngredient.save_to_file(file_name, format)
            file_name = f'{path}/{cls.FAVORITE_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            Favorite.save_to_file(file_name, format)
            file_name = f'{path}/{cls.SHOPPING_FILE}{cls.EXT[format]}'
            print(f'export data to `{file_name}`')
            Shopping.save_to_file(file_name, format)
        except Exception as error:
            raise CommandError(f'error: {type(error)} = {error}')
