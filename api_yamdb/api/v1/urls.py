from django.urls import include, path
from rest_framework import routers

from .views import ReviewsViewSet, CommentsViewSet

router = routers.DefaultRouter()

router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
]
