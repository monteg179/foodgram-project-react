from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (
    Favorite,
    Shopping,
)
from users.models import (
    FoodgramUser,
    Subscription,
)


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0


class ShoppingInline(admin.TabularInline):
    model = Shopping
    extra = 0


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    fk_name = 'user'
    extra = 0


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):

    list_display = ('id', 'username', 'email', 'first_name', 'last_name',
                    'is_active', 'is_staff', 'is_superuser')
    inlines = (FavoriteInline, ShoppingInline, SubscriptionInline)
    list_filter = ('username', 'email')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2'
            ),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
