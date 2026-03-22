from django.contrib import admin
from .models import Post, Category, Subscriber

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'category')
    list_filter = ('status', 'created', 'publish', 'author', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish'
    ordering = ('status', '-publish')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'confirmed', 'subscribed_at', 'confirmed_at')
    list_filter = ('confirmed',)
    search_fields = ('email',)
    readonly_fields = ('token', 'subscribed_at', 'confirmed_at')
    ordering = ('-subscribed_at',)