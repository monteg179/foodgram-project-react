from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import FoodgramUser, Subscription


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):

    list_display = ('id', 'username', 'email', 'first_name', 'last_name',
                    'is_active', 'is_staff', 'is_superuser')

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
