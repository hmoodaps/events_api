from rest_framework import permissions

class CanCreateReservationPermission(permissions.BasePermission):
    """
    صلاحية مخصصة للضيف تتيح فقط إنشاء الحجز.
    """

    def has_permission(self, request, view):
        # السماح للضيوف فقط الذين لديهم التوكن المخصص
        if request.user and request.user.is_authenticated:
            # التأكد من أن المستخدم ينتمي إلى مجموعة الضيوف
            return request.user.groups.filter(name='Guests').exists()
        return False
