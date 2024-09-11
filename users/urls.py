from django.urls import path, include

from .views import *

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('agent-auth/', AgentAuth.as_view(), name='agent_login'),
    path('get-agent-details/', getAgentDetails.as_view(), name='agent_details'),
    path('get-credit-users/', GetCreditUsers.as_view(),name='credit_users'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Manage users API
    path('users/', UserCreateView.as_view(), name='create_user'),
    path('users/<str:email>', GetUserDetails.as_view(), name='get_user_details'),
    path('get-all-users/', GetAllUsers.as_view(), name='get_all_users'),
    #TODO add update user API

    # path('update-user/', UpdateUserView.as_view(), name='update_user'),
    path('reset-password/<int:userId>', ResetPasswordView.as_view(), name='reset_password'),

    # Manage main branches APIs
    path('branches', BranchCreateView.as_view(), name='create_branch'),
    path('branches/<str:branch_name>', GetBranchDetailsView.as_view(), name='get_branch_details'),
    path('get-branches', BranchListView.as_view(), name='get_branches'),
    path('get-branch/<int:id>', GetBranchView.as_view(), name='get_branch_by_id'),

    path('satellite-branch', CreateSatelliteBranchView.as_view(), name='create_satellite_branch'),
    path('satellite-branch/<int:id>', GetSatelliteBranchView.as_view(), name='get_satellite_by_id'),
    path('get-satellite-branch/<str:name>', GetSatelliteBranchDetailsView.as_view(), name='get_satellite_by_id'),
    path('get-satellite-branches', SatelliteBranchListView.as_view(), name='get-satellite-branches'),

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
