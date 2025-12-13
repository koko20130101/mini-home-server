from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsReader(permissions.BasePermission):
    def has_permission(self, request, view):
        master = request.GET.get('reader') or request.data.get('reader')
        return bool(request.user and request.user.id == master)


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            return False


class IsOwner(permissions.BasePermission):
    # 只有调视图集的详情时才过这里retrieve
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
