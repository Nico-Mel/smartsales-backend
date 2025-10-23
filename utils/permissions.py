from rest_framework import permissions
from .exceptions import PermissionDeniedException

class ModulePermission(permissions.BasePermission):
    """
    Revisa si el usuario tiene permiso para realizar la acción sobre un módulo.
    Cada modelo que represente un "módulo" debe registrar sus permisos en la tabla Module + Permission.
    """

    action_map = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'create',
        'update': 'update',
        'partial_update': 'update',
        'destroy': 'delete'
    }

    def has_permission(self, request, view):
        user = request.user
        module_name = getattr(view, 'module_name', None)
        action = getattr(view, 'action', None)
        required_permission = self.action_map.get(action)

        # Usuario no autenticado
        if not user.is_authenticated:
            raise PermissionDeniedException()

        # Admin tiene todos los permisos
        if getattr(user.role, 'name', None) == "ADMIN":
            return True

        # Validar módulo, acción y rol
        if not module_name or not user.role or not required_permission:
            raise PermissionDeniedException()

        # Revisa si el rol del usuario tiene ese permiso en el módulo
        if not user.role.privileges.filter(
            module__name=module_name,
            **{f'can_{required_permission}': True}
        ).exists():
            raise PermissionDeniedException()

        return True
