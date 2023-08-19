from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoriesViewSet, CommentsViewSet, ConfirmationView,
                    GenresViewSet, ReviewsViewSet, SignupView, TitlesViewSet,
                    UserViewSet)

router = SimpleRouter()
router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)
router.register('titles', TitlesViewSet)
router.register('users', UserViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', SignupView.as_view()),
    path('auth/token/', ConfirmationView.as_view())
]
