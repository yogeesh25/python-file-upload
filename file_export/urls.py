
from django.urls.conf import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns=[
    path('file_upload',views.FileUploadAPI.as_view(),name='file_upload'),
    path('task/<str:task_id>/', views.TaskView.as_view(), name='task'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]