from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManagerOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        
        if request.user.is_authenticated:
            is_manager = request.user.groups.filter(name='Manager').exists()
            is_admin = request.user.is_staff or request.user.is_superuser
            return is_manager or is_admin
        
        return False


class IsManagerOrAdmin(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.groups.filter(name='Manager').exists() or (
                request.user.is_staff or request.user.is_superuser
            )
        )
    
class IsCustomerOrManager(BasePermission):
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.groups.filter(name='Manager').exists():
            return True

        if request.user.is_staff or request.user.is_superuser:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)
        is_customer = not any(group in ['Manager', 'Delivery Crew'] for group in user_groups)
        return is_customer
    
    def has_object_permission(self, request, view, obj):
        if (request.user.groups.filter(name='Manager').exists() or 
            request.user.is_staff or request.user.is_superuser):
            return True

        return obj.user == request.user

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery Crew').exists()

class isCustomer(BasePermission):
    def has_permission(self, request, view):
        return not request.user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists()