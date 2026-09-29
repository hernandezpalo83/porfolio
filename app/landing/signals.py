"""
Cache invalidation for the landing: any change to the models shown on the home
bumps the 'landing' content-cache version (see app.utils.content_cache). The
home also follows the 'blog' version for its latest posts.
"""
from app.utils.content_cache import register

from .models import CompanyCollaboration, CredlyBadge, Education, Experience, Info, Metric, Project, Skill, Technology

register('landing', Info, Skill, Experience, Education, Project, Metric, CompanyCollaboration, Technology, CredlyBadge)
