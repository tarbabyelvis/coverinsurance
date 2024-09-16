from django.urls import path, include

from .views import *

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Manage users API
    path('users/', UserCreateView.as_view(), name='create_user'),
    path('users/<str:email>', GetUserDetails.as_view(), name='get_user_details'),
    path('get-all-users/', GetAllUsers.as_view(), name='get_all_users'),
    path('reset-password/<int:userId>', ResetPasswordView.as_view(), name='reset_password'),

    path('permissions', GetPermissionsView.as_view(), name='get_permissions'),
    path('create-permissions', CreatePermissionView.as_view(), name='create_permissions'),
    path('permissions/<int:userId>', AddOrRemovePermissionsToUserView.as_view(), name='add_or_remove_user_permissions'),
    path('create-groups', CreateGroupView.as_view(), name='create_groups'),
    path('update-groups/<int:groupId>', UpdateGroupView.as_view(), name='update_groups'),
    path('groups/<int:userId>', AddOrRemoveGroupsView.as_view(), name='add_or_remove_user_groups'),
    path('groups', GetGroupsView.as_view(), name='get_groups'),
    path('groups-details/<int:groupId>', GetGroupDetailsView.as_view(), name='get-group-details'),
    path('contenttype', CreateContentTypeView.as_view(), name='create_content_type'),
    path('contenttypes', ListContentTypeView.as_view(), name='list_content_type'),

]
