import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.config.settings')
django.setup()

from app.docs.models import Category, Document

def seed_docs():
    print("🌱 Seeding Documentation Hub...")
    
    # 1. Create Categories
    categories_data = [
        {
            'name': 'Infrastructure',
            'description': 'DevOps, Cloud (AWS/Render), security and deployment pipelines.',
            'icon': 'fa-server',
            'order': 1
        },
        {
            'name': 'Backend Engineering',
            'description': 'Django best practices, API design, and database optimizations.',
            'icon': 'fa-cogs',
            'order': 2
        },
        {
            'name': 'Product Strategy',
            'description': 'TPM methodology, product discovery, and technical leadership.',
            'icon': 'fa-lightbulb',
            'order': 3
        }
    ]
    
    cats = {}
    for data in categories_data:
        cat, created = Category.objects.get_or_create(name=data['name'], defaults=data)
        cats[data['name']] = cat
        if created:
            print(f"Created category: {cat.name}")

    # 2. Create Sample Documents
    docs_data = [
        {
            'title': 'Django Production Optimization Checklist',
            'category': cats['Backend Engineering'],
            'status': 'published',
            'stack_version': 'Django 5.1, Python 3.12',
            'meta_description': 'Essential checklist for deploying high-performance Django applications in production.',
            'content_markdown': """# Django Production Optimization Checklist

This document outlines the essential steps for taking a Django application from development to a professional production environment.

## 1. Security First
- [x] Set `DEBUG = False`
- [x] Use environment variables for `SECRET_KEY`
- [x] Configure `ALLOWED_HOSTS`

## 2. Performance Core
### Static Files
Use WhiteNoise for serving static files efficiently:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]
```

### Database
Ensure you are using `conn_max_age` for persistent connections.

## 3. SEO & UX
Don't forget to implement standard sitemaps and compressed static assets.
"""
        },
        {
            'title': 'The TPM Transition: From Developer to Product Leader',
            'category': cats['Product Strategy'],
            'status': 'published',
            'stack_version': 'Product Methodology',
            'meta_description': 'A guide for senior developers transitioning into Technical Product Management roles.',
            'content_markdown': """# The TPM Transition

Moving from writing code to managing product technical strategy requires a significant shift in mindset.

## Key Focus Areas
1. **Stakeholder Management**: Translating technical complexity into business value.
2. **Prioritization**: Understanding the "Cost of Delay".
3. **Documentation**: Creating technical roadmaps that align with business goals.

> "A great TPM doesn't just manage tasks; they bridge the gap between engineering reality and product vision."

### Recommended Stack
- Agile/Scrum
- Product Discovery Frameworks
- Technical Architecture Docs
"""
        }
    ]
    
    for data in docs_data:
        doc, created = Document.objects.get_or_create(title=data['title'], defaults=data)
        if created:
            print(f"Created document: {doc.title}")
        else:
            # Force re-save to trigger markdown rendering
            doc.save()

    print("✅ Seeding complete!")

if __name__ == "__main__":
    seed_docs()
