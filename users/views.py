import asyncio

from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from loans.supabase import send_to_comms_log
from loans.tasks import send_emails, sendEmailTask
from supabase_util.utils import get_organization_by_org_id
from .models import *
from .serializers import UserSerializer, BranchSerializer, SatelliteSerializer, PermissionRequest, GroupSerializer, \
    ContentTypeSerializer, PermissionSerializer, convert_to_name
from .utils import normalize_email, BaseResponse, PaginationHandlerMixin, Pagination, PaginationResponse


class UserCreateView(APIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

    def post(self, request):
        branchId = request.data['branch']
        try:
            branch = SatelliteBranch.objects.get(id=branchId)
            branch_dict = {
                "id": branch.id,
                "name": branch.name,
                "email": branch.email,
                "is_active": branch.is_active,
                "town": branch.town,
                "branch": {
                    "id": branch.branch.id,
                    "name": branch.branch.name,
                    "email": branch.branch.email,
                    "is_active": branch.branch.is_active,
                    "town": branch.branch.town,
                },
            }
        except SatelliteBranch.DoesNotExist:
            message = "Branch not found %s" % branchId
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_400_BAD_REQUEST)

        request.data['branch'] = branch_dict
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
                organisation = get_organization_by_org_id(tenant_id)
                send_to_comms_log(28, request.data['email'], message, organisation.get("id"))
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


class AgentAuth(APIView):
    def post(self, request):
        mobile = request.data.get("mobile", "")
        agent_code = request.data.get("agent_code", "")

        # make sure certain field are not blank
        formatted_phone = ""
        try:
            # if mobile[0] == '0':
            #     formatted_phone = '254'+mobile[1:]
            # elif mobile[0] == '+':
            #     formatted_phone = mobile[1:]
            # else:
            #     formatted_phone = mobile
            formatted_phone = mobile

        except Exception as e:
            print(e)
            return Response("Invalid phone number", status=status.HTTP_401_UNAUTHORIZED)

        if formatted_phone == "" or agent_code == "":
            print("parameters not correct")
            return Response(
                "Incorrect credentials", status=status.HTTP_401_UNAUTHORIZED
            )

        else:
            user = Profile.objects.filter(
                user__phone=formatted_phone, access_code__iexact=agent_code
            )
            # user = Profile.objects.filter(access_code__iexact=agent_code)
            # user = Profile.objects.filter(user__phone=formatted_phone, access_code=agent_code)
            if user.exists():  # user is authenticated
                print(
                    "User exists: ",
                    user.values("id", "user__first_name", "code", "access_code"),
                )
                return Response(
                    user.values(
                        "user__id",
                        "user__first_name",
                        "code",
                        "access_code",
                        "user__last_name",
                        "user__phone",
                    )[0],
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                print("login failed, user was not found")
                print("Failed to fetch the client")
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)


class getAgentDetails(APIView):
    def post(self, request):
        agent_id = request.data.get("tg_agent_code", "")

        if agent_id == "":
            print("parameters not correct")
            return Response("error", status=status.HTTP_400_BAD_REQUEST)

        else:
            user = Profile.objects.filter(access_code=agent_id)
            if user.exists():  # user is authenticated
                print("User exists: ", user.values("id", "access_code"))
                return Response(
                    user.values(
                        "user__id",
                        "access_code",
                        "user__first_name",
                        "user__last_name",
                        "user__phone",
                    )[0],
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                print("login failed, user was not found")
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)


class GetCreditUsers(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        users = (
            User.objects.filter(
                Q(user_type="admin")
                | Q(user_type="credit_team_leader")
                | Q(user_type="credit_analysis")
                | Q(user_type="credit_admin")
                | Q(user_type="credit_manager")
            )
            .filter(is_active__icontains=True)
            .order_by("first_name")
            .values(
                "id",
                "is_teamleader",
                "is_supervisor",
                "first_name",
                "last_name",
                "email",
                "user_type",
            )
        )
        return Response(users, status=status.HTTP_202_ACCEPTED)


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
        isActive = request.query_params.get('is_active')
        email = request.query_params.get('email')
        branch = request.query_params.get('branch')
        userType = request.query_params.get("user_type")
        query = request.query_params.get("query")

        filters = Q()
        if isActive is not None:
            filters &= Q(is_active=isActive)
        if email:
            filters &= Q(email=email)
        if branch:
            filters &= Q(branch=branch)
        if userType:
            filters &= Q(user_type=userType)

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
            finalList = self.paginate_queryset(users)
            pageSize = len(finalList)
            return Response(BaseResponse(data=finalList, message="Success", status=200,
                                         pagination=PaginationResponse(page_size=pageSize, count=count,
                                                                       page=page).to_dict()
                                         ).to_dict(),
                            status=status.HTTP_200_OK)
        except Exception as e:
            message = "Users not found error: %s" % e
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class BranchCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(BaseResponse(data=serializer.data,
                                         message="Branch created successfully", status=201).to_dict(),
                            status=status.HTTP_201_CREATED)
        return Response(BaseResponse(data=serializer.errors, message="Failed to create a branch", status=400).to_dict(),
                        status=status.HTTP_400_BAD_REQUEST)


class GetBranchDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        name = kwargs.get("branch_name")
        try:
            data = Branch.objects.get(name=name)
            serializer = BranchSerializer(data)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        except Branch.DoesNotExist:
            message = "Branch does not exist: %s" % name
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class GetBranchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        branchId = kwargs.get("id")
        try:
            data = Branch.objects.get(id=branchId)
            serializer = BranchSerializer(data)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        except Branch.DoesNotExist:
            message = "Branch does not exist: %s" % branchId
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class BranchListView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        town = request.query_params.get("town")
        isActive = request.query_params.get("is_active")
        filters = Q()
        if town is not None:
            filters &= Q(town=town)
        if isActive:
            filters &= Q(is_active=isActive)
        try:
            branches = (
                Branch.objects.all()
                .filter(filters)
                .order_by("-created")
                .values(
                    "id",
                    "town",
                    "name",
                    "email",
                    "is_active",
                    "created",
                )
            )
            page = int(self.request.query_params.get("page", 1))
            count = branches.count()
            finalList = self.paginate_queryset(branches)
            pageSize = len(finalList)
            return Response(
                BaseResponse(
                    data=finalList,
                    message="Success",
                    status=200,
                    pagination=PaginationResponse(
                        page_size=pageSize, count=count, page=page
                    ).to_dict(),
                ).to_dict(),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = "Branches not found, error: %s" % e
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )


class CreateSatelliteBranchView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        branchId = request.data["branch"]
        try:
            branch = Branch.objects.get(id=branchId)

        except Branch.DoesNotExist:
            message = "Branch does not exist: %s" % branchId
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )
        branch_dict = {
            "name": branch.name,
            "email": branch.email,
            "is_active": branch.is_active,
            "town": branch.town,
            "id": branch.id,
        }
        request.data["branch"] = branch_dict
        serializer = SatelliteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                BaseResponse(
                    data=serializer.data,
                    message="Satellite Branch created successfully",
                    status=201,
                ).to_dict(),
                status=status.HTTP_201_CREATED,
            )
        return Response(
            BaseResponse(data=serializer.errors, message="Failed to create a satellite branch", status=400).to_dict(),
            status=status.HTTP_400_BAD_REQUEST)


class GetSatelliteBranchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        branchId = kwargs.get("id")
        try:
            data = SatelliteBranch.objects.get(id=branchId)
            serializer = SatelliteSerializer(data)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        except SatelliteBranch.DoesNotExist:
            message = "Satellite Branch does not exist: %s" % branchId
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class GetSatelliteBranchDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        name = kwargs.get("name")
        try:
            data = SatelliteBranch.objects.get(name=name)
            serializer = SatelliteSerializer(data)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        except SatelliteBranch.DoesNotExist:
            message = "Satellite Branch does not exist: %s" % name
            return Response(BaseResponse(message=message, status=404).to_dict(), status=status.HTTP_404_NOT_FOUND)


class SatelliteBranchListView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        town = request.query_params.get("town")
        isActive = request.query_params.get("is_active")
        filters = Q()
        if town is not None:
            filters &= Q(town=town)
        if isActive:
            filters &= Q(is_active=isActive)
        try:
            branches = (
                SatelliteBranch.objects.all()
                .filter(filters)
                .order_by("-created")
                .values(
                    "id",
                    "town",
                    "name",
                    "email",
                    "branch__id",
                    "branch__name",
                    "is_active",
                    "created",
                )
            )

            page = int(self.request.query_params.get("page", 1))
            count = branches.count()
            finalList = self.paginate_queryset(branches)
            pageSize = len(finalList)
            return Response(
                BaseResponse(
                    data=finalList,
                    message="Success",
                    status=200,
                    pagination=PaginationResponse(
                        page_size=pageSize, count=count, page=page
                    ).to_dict(),
                ).to_dict(),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = "Satellite branches not found, error: %s" % e
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPermissionsView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request):
        userType = request.query_params.get("content_type", "custom")
        filters = Q()
        if userType is not None:
            filters &= Q(content_type__app_label__icontains=userType)
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
            finalList = self.paginate_queryset(permissions)
            pageSize = len(finalList)
            return Response(
                BaseResponse(
                    data=finalList,
                    message="Success",
                    status=200,
                    pagination=PaginationResponse(
                        page_size=pageSize, count=count, page=page
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
        userId = kwargs.pop("userId", None)
        action = request.query_params.get("action", None)
        if action not in ["add", "remove"] or action is None:
            return Response(
                BaseResponse(
                    message="Action must be add or remove", status=400
                ).to_dict(),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            message = "User does not exist: %s" % userId
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )

        codeNameList = request.data["permissions"]
        if codeNameList:
            permissions = Permission.objects.filter(codename__in=codeNameList)
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
            finalList = self.paginate_queryset(list(grouped_groups))
            pageSize = len(finalList)
            return Response(
                BaseResponse(
                    data=finalList,
                    message="Success",
                    status=200,
                    pagination=PaginationResponse(
                        page_size=pageSize, count=count, page=page
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
        groupId = kwargs.pop("groupId", None)
        try:
            group = Group.objects.get(id=groupId)
            serializer = GroupSerializer(group)
            return Response(
                BaseResponse(
                    data=serializer.data, message="Success", status=200
                ).to_dict(),
                status=status.HTTP_200_OK,
            )
        except Group.DoesNotExist:
            message = "Group does not exist: %s" % groupId
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )


class AddOrRemoveGroupsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        userId = kwargs.get("userId")
        action = request.query_params.get("action", None)
        if action not in ["add", "remove"] or action is None:
            return Response(
                BaseResponse(
                    message="Action must be add or remove", status=400
                ).to_dict(),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            message = "User does not exist: %s" % userId
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )

        groupNameList = request.data["groups"]
        if groupNameList:
            groups = Group.objects.filter(name__in=groupNameList)
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
        userId = kwargs.get("userId")

        newpassword = request.data["new_password"]
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            message = "User does not exist: %s" % userId
            return Response(
                BaseResponse(message=message, status=404).to_dict(),
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(newpassword)
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
                    f"{newpassword}",
                ]
            }
        }
        organisation = get_organization_by_org_id(tenant_id)
        send_to_comms_log(29, request.data['email'], message, organisation.get("id"))
        return Response(BaseResponse(message=message1, status=200).to_dict(), status=status.HTTP_200_OK)


class CreatePermissionView(APIView):

    def post(self, request):

        name = request.data['name']
        model = request.data['model']
        codeName = request.data['code_name']
        try:
            contentType = ContentType.objects.get(model=model)
        except ContentType.DoesNotExist:
            return Response(BaseResponse(message="Content type does not exist", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)
        perm = Permission.objects.create(
            name=name,
            content_type=contentType,
            codename=codeName,
        )

        serializer = PermissionSerializer(perm)
        return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                        status=status.HTTP_200_OK)


class CreateContentTypeView(APIView):

    def post(self, request):
        appLabel = request.data['app_label']
        model = request.data['model']
        try:
            exists = ContentType.objects.get(model=model)
            if exists.id is not None:
                return Response(BaseResponse(message="Content type already exists", status=400).to_dict(),
                                status=status.HTTP_400_BAD_REQUEST)
        except ContentType.DoesNotExist:
            pass
        ct = ContentType.objects.create(
            app_label=appLabel,
            model=model,
        )
        serializer = ContentTypeSerializer(ct)
        return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                        status=status.HTTP_200_OK)


class ListContentTypeView(APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        appLabel = request.query_params.get("app_label")
        filters = Q()
        if appLabel is not None:
            filters &= Q(app_label=appLabel)
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
            finalList = self.paginate_queryset(types)
            pageSize = len(finalList)
            return Response(BaseResponse(data=finalList, message="Success", status=200,
                                         pagination=PaginationResponse(page_size=pageSize, count=count,
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
        permissionList = request.data['permissions']

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

        if permissionList:
            for permission in permissionList:
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
        groupId = kwargs.pop('groupId', None)
        name = request.data['name']
        permissions = request.data['permissions']
        try:
            groupToUpdate = Group.objects.get(id=groupId)
        except Group.DoesNotExist:
            return Response(BaseResponse(message="Group does not exist", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)
        groupToUpdate.name = name
        groupToUpdate.permissions.clear()
        if permissions:
            for permission in permissions:
                try:
                    perm, _ = Permission.objects.get_or_create(
                        codename=permission,
                        defaults={
                            "content_type": ContentType.objects.get(model="custom"),
                            "name": convert_to_name(permission),
                        })
                    groupToUpdate.permissions.add(perm)
                except Exception:
                    return Response(BaseResponse(message="Could not find permission", status=400).to_dict(),
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer = GroupSerializer(groupToUpdate)
            return Response(BaseResponse(data=serializer.data, message="Success", status=200).to_dict(),
                            status=status.HTTP_200_OK)
        else:
            return Response(BaseResponse(message="No permissions provided", status=400).to_dict(),
                            status=status.HTTP_400_BAD_REQUEST)
