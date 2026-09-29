"""
Cache invalidation for the blog: any change to posts or categories bumps the
'blog' content-cache version (listing, detail, related posts and the home
preview all read from it). See app.utils.content_cache.
"""
from app.utils.content_cache import register

from .models import Category, Post

register('blog', Post, Category)
