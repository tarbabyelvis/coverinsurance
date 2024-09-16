from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import UserSerializer, PermissionRequest, GroupSerializer, \
    ContentTypeSerializer, PermissionSerializer, convert_to_name
from .utils import normalize_email, BaseResponse, PaginationHandlerMixin, Pagination, PaginationResponse


class UserCreateView(APIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

    def post(self, request):

        request.data['permissions'] = PermissionRequest(request.data['permissions'], request.data["groups"]).to_dict()
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # send email to user
            try:
                print("Sending email to user")
                email = request.data['email'].split(",")
                password = request.data['password']
                tenant_id = str(request.tenant).replace("-", "_")
                origin = request.headers.get('Origin', "")
                url = origin + "?tenant=%s" % tenant_id
                message = {
                    "values": {
                        "subject": "Account Creation for Fin Connect",
                        "variables": [
                            f"{url}",
                            f"{email}",
                            f"{password}",
                        ]
                    }
                }
            except Exception as e:
                print("Error sending email", e)
                pass
            return Response(
                BaseResponse(data=serializer.data, message="User created successfully", status=200).to_dict(),
                status=status.HTTP_201_CREATED)
        return Response(BaseResponse(data=serializer.errors, message="Failed to create a user", status=400).to_dict(),
                        status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(
            self,
            request,
    ):
        email = normalize_email(request.data.get("email"))
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user:
            print(UserSerializer(user).data)
            return Response(
                {"token": user.auth_token.key, "user": UserSerializer(user).data},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"error": "Wrong credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class GetUserDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        email = kwargs.get("email")
        try:
            data = User.objects.get(email=email)
            serializer = UserSerializer(data)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            message = "User does not exist: %s" % email
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class GetAllUsers(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        is_active = request.query_params.get('is_active')
        email = request.query_params.get('email')
        user_type = request.query_params.get("user_type")
        query = request.query_params.get("query")

        filters = Q()
        if is_active is not None:
            filters &= Q(is_active=is_active)
        if email:
            filters &= Q(email=email)
        if user_type:
            filters &= Q(user_type=user_type)

        if query:
            filters &= (
                    Q(first_name__icontains=query)
                    | Q(last_name__icontains=query)
                    | Q(email__icontains=query)
            )
        try:
            users = (
                User.objects.all()
                .filter(filters)
                .order_by("-date_joined")
                .values(
                    "id",
                    "is_teamleader",
                    "is_supervisor",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "user_type",
                    "date_joined",
                    "branch__name",
                    "is_active",
                )
            )
            page = int(self.request.query_params.get("page", 1))
            count = users.count()
            final_list = self.paginate_queryset(users)
            page_size = len(final_list)
            return Response(BaseResponse(data=final_list, message="Success", status=200,
                                         pagination=PaginationResponse(page_size=page_size, count=count,
                                                                       page=page).to_dict()
                                         ).to_dict(),
                            status=status.HTTP_200_OK)
        except Exception as e:
            message = "Users not found error: %s" % e
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class GetPermissionsView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request):
        user_type = request.query_params.get("content_type", "custom")
        filters = Q()
        if user_type is not None:
            filters &= Q(content_type__app_label__icontains=user_type)
        try:
            permissions = (
                Permission.objects.all()
                .filter(filters)
                .order_by("id")
                .values(
                    "id",
                    "name",
                    "content_type__app_label",
                    "codename",
                )
            )

            page = int(self.request.query_params.get("page", 1))
            count = permissions.count()
            final_list = self.paginate_queryset(permissions)
            page_size = len(final_list)
            return Response(
                BaseResponse(
                    data=final_list,
                    message="Success",
                    status=200,
                    pagination=PaginationResponse(
                        page_size=page_size, count=count, page=page
                    ).to_dict(),
                ).to_dict(),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = "Permissions not found, error: %s" % e
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )


class AddOrRemovePermissionsToUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.pop("userId", None)
        action = request.query_params.get("action", None)
        if action not in ["add", "remove"] or action is None:
            return Response(
                BaseResponse(
                    message="Action must be add or remove", status=400
                ).to_dict(),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            message = "User does not exist: %s" % user_id
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )

        code_names = request.data["permissions"]
        if code_names:
            permissions = Permission.objects.filter(codename__in=code_names)
            if action == "add":
                user.user_permissions.set(permissions)
            elif action == "remove":
                user.user_permissions.remove(*permissions)
            user.save()
            mes = "Permissions modified successfully with action: %s" % action
            status_code = 200
        else:
            mes = "No permissions to modify"
            status_code = 400
        return Response(
            BaseResponse(message=mes, status=status_code).to_dict(),
            status=status.HTTP_200_OK,
        )


class GetGroupsView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination
    serializer_class = GroupSerializer

    def get(self, request):
        name = request.query_params.get("name")
        filters = Q()
        if name is not None:
            filters &= Q(name=name)

        try:
            groups = (
                Group.objects.all()
                .filter(filters)
                .order_by("id")
                .values(
                    "id",
                    "name",
                    "permissions",
                )
            )
            group_ids = list({group['id'] for group in groups})
            group_permissions = {}

            for group_id in group_ids:
                group_permissions[group_id] = []

            for group in groups:
                permissions = Permission.objects.filter(id=group['permissions'])
                serialized_permissions = PermissionSerializer(permissions, many=True).data
                group_permissions[group['id']].extend(serialized_permissions)

            # Now group each group with its permissions
            grouped_groups = list([])
            for groupId in group_ids:
                for group in groups:
                    if groupId == group['id']:
                        grouped_group = {
                            'id': groupId,
                            'name': group['name'],
                            'permissions': group_permissions[groupId]
                        }
                        grouped_groups.append(grouped_group)
                        break  # This will stop searching for the current group

            page = int(self.request.query_params.get("page", 1))
            count = len(list(grouped_groups))
            final_list = self.paginate_queryset(list(grouped_groups))
            page_size = len(final_list)
            return Response(
                BaseResponse(
                    data=final_list,
                    message="Success",
                    status=200,
                    pagination=PaginationResponse(
                        page_size=page_size, count=count, page=page
                    ).to_dict(),
                ).to_dict(),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = "Groups not found, error: %s" % e
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )


class GetGroupDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        group_id = kwargs.pop("groupId", None)
        try:
            group = Group.objects.get(id=group_id)
            serializer = GroupSerializer(group)
            return Response(
                BaseResponse(
                    data=serializer.data, message="Success", status=200
                ).to_dict(),
                status=status.HTTP_200_OK,
            )
        except Group.DoesNotExist:
            message = "Group does not exist: %s" % group_id
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )


class AddOrRemoveGroupsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("userId")
        action = request.query_params.get("action", None)
        if action not in ["add", "remove"] or action is None:
            return Response(
                BaseResponse(
                    message="Action must be add or remove", status=400
                ).to_dict(),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            message = "User does not exist: %s" % user_id
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )

        group_names = request.data["groups"]
        if group_names:
            groups = Group.objects.filter(name__in=group_names)
            if action == "add":
                user.groups.set(groups)
            elif action == "remove":
                user.groups.remove(*groups)
            user.save()
            mes = "Groups modified successfully with action: %s" % action
            status_code = 200
        else:
            mes = "No groups to modify"
            status_code = 400
        return Response(
            BaseResponse(message=mes, status=status_code).to_dict(),
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("userId")

        new_password = request.data["new_password"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            message = "User does not exist: %s" % user_id
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(new_password)
        user.save()
        message1 = "Password changed successfully"
        # send email to user
        email = user.email.split(",")
        tenant_id = str(request.tenant).replace("-", "_")
        origin = request.headers.get("Origin", "")
        url = origin + "?tenant=%s" % tenant_id

        message = {
            "values": {
                "subject": "Password Reset",
                "variables": [
                    f"{url}",
                    f"{email}",
                    f"{new_password}",
                ]
            }
        }
        return Response(BaseResponse(message=message1, status=200).to_dict(), status=status.HTTP_200_OK)


class CreatePermissionView(APIView):

    def post(self, request):

        name = request.data['name']
        model = request.data['model']
        code_name = request.data['code_name']
        try:
            content_type = ContentType.objects.get(model=model)
        except ContentType.DoesNotExist:
            return Response(BaseResponse(message="Content type does not exist", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)
        perm = Permission.objects.create(
            name=name,
            content_type=content_type,
            codename=code_name,
        )

        serializer = PermissionSerializer(perm)
        return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                        status=status.HTTP_200_OK)


class CreateContentTypeView(APIView):

    def post(self, request):
        app_label = request.data['app_label']
        model = request.data['model']
        try:
            exists = ContentType.objects.get(model=model)
            if exists.id is not None:
                return Response(BaseResponse(message="Content type already exists", status=400).to_dict(),
                                status=status.HTTP_400_BAD_REQUEST)
        except ContentType.DoesNotExist:
            pass
        ct = ContentType.objects.create(
            app_label=app_label,
            model=model,
        )
        serializer = ContentTypeSerializer(ct)
        return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                        status=status.HTTP_200_OK)


class ListContentTypeView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        app_label = request.query_params.get("app_label")
        filters = Q()
        if app_label is not None:
            filters &= Q(app_label=app_label)
        try:
            types = (
                ContentType.objects.all()
                .filter(filters)
                .values(
                    "id",
                    "model",
                    "app_label",
                ))

            page = int(self.request.query_params.get("page", 1))
            count = types.count()
            final_list = self.paginate_queryset(types)
            page_size = len(final_list)
            return Response(BaseResponse(data=final_list, message="Success", status=200,
                                         pagination=PaginationResponse(page_size=page_size, count=count,
                                                                       page=page).to_dict()
                                         ).to_dict(),
                            status=status.HTTP_200_OK)
        except Exception as e:
            message = "Content Types not found, error: %s" % e
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class CreateGroupView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        group = {}
        name = request.data['name']
        permissions = request.data['permissions']

        try:
            group = Group.objects.get(name=name)
            if group.id is not None:
                return Response(BaseResponse(message="Group already exists", status=400).to_dict(),
                                status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            pass

        group = Group.objects.create(
            name=name,
        )

        if permissions:
            for permission in permissions:
                try:
                    perm, _ = Permission.objects.get_or_create(
                        codename=permission,
                        defaults={
                            "content_type": ContentType.objects.get(model="custom"),
                            "name": convert_to_name(permission),
                        })
                    group.permissions.add(perm)
                except Exception:
                    return Response(BaseResponse(message="Could not find permission", status=400).to_dict(),
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer = GroupSerializer(group)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        else:
            return Response(BaseResponse(message="No permissions provided", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)


class UpdateGroupView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        group_id = kwargs.pop('groupId', None)
        name = request.data['name']
        permissions = request.data['permissions']
        try:
            group_to_update = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(BaseResponse(message="Group does not exist", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)
        group_to_update.name = name
        group_to_update.permissions.clear()
        if permissions:
            for permission in permissions:
                try:
                    perm, _ = Permission.objects.get_or_create(
                        codename=permission,
                        defaults={
                            "content_type": ContentType.objects.get(model="custom"),
                            "name": convert_to_name(permission),
                        })
                    group_to_update.permissions.add(perm)
                except Exception:
                    return Response(BaseResponse(message="Could not find permission", status=400).to_dict(),
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer = GroupSerializer(group_to_update)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        else:
            return Response(BaseResponse(message="No permissions provided", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)
