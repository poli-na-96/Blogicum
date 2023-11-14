from django.contrib import admin

from .models import Category, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
        'pub_date',

    )
    list_editable = (
        'is_published',
        'pub_date',
    )
    search_fields = ('title', 'author', 'location',)
    list_filter = ('is_published', 'created_at',)
    list_display_links = ('title', 'author', 'location',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
