from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Categories, Comment, Genres, Review, Titles

User = get_user_model()


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser',
                                    'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),

    )


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('review', 'text', 'author',)
    list_filter = ('review', 'author',)
    empty_value_display = '-пусто-'


class GenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'description')
    search_fields = ('name', 'slug')
    list_filter = ('year', 'category',)
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'author', 'pub_date', 'score')
    search_fields = ('title', 'text', 'author')
    list_filter = ('title', 'author')
    empty_value_display = '-пусто-'


admin.site.register(User, MyUserAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genres, GenresAdmin)
admin.site.register(Titles, TitlesAdmin)
admin.site.register(Review, ReviewAdmin)
