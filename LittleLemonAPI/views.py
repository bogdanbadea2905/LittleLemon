from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status
from .models import MenuItem, Category, Cart, Order, OrderItem, Booking
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from django.contrib.auth.models import User, Group
from .permissions import IsManagerOrReadOnly, IsManagerOrAdmin, IsCustomerOrManager
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .forms import BookingForm
from datetime import datetime
from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json



# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]

class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['category']
    search_fields = ['category__title']
    

    # def get_permissions(self):
    #     permission_classes = []
    #     if self.request.method == 'PUT' or self.request.method == 'PATCH' or self.request.method == 'DELETE' or self.request.method == 'POST':
    #         permission_classes = [IsAuthenticated]
        
    #     return [permission() for permission in permission_classes]
    permission_classes = [IsManagerOrReadOnly]

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.RetrieveDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]

def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = MenuItem.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data)

    username = request.data.get('username')
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == 'POST':
            managers.user_set.add(user)
            return Response({"message": f"User {username} added to Managers"}, 201)
    else:
        return Response({"error": "Username required"}, 400)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_manager(request, userId):
    user = get_object_or_404(User, pk=userId)
    managers = Group.objects.get(name="Manager")
    managers.user_set.remove(user)
    return Response({"message": "User removed from Managers"}, 200)

@api_view(['GET', 'POST'])
@permission_classes([IsManagerOrAdmin])
def delivery_crew(request):
    if request.method == 'GET':
        delivery = User.objects.filter(groups__name='Delivery Crew')
        serializer = UserSerializer(delivery, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        username = request.data.get('username')
        if not username: 
            return Response({"error": "Username required"}, 400)
        user = get_object_or_404(User, username=username)
        delivery = Group.objects.get(name="Delivery Crew")
        delivery.user_set.add(user)
        return Response({"message": f"User {username} added to Delivery Crew"}, 201)

@api_view(['DELETE'])
@permission_classes([IsManagerOrAdmin])
def remove_delivery(request, userId):
    user = get_object_or_404(User, pk=userId)
    delivery = Group.objects.get(name="Delivery Crew")
    delivery.user_set.remove(user)
    return Response({"message": "User removed from Delivery Crew"}, 200)


class CartMenuItemsView(generics.ListCreateAPIView, generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsCustomerOrManager]
    
    def get_queryset(self):
        if (self.request.user.groups.filter(name='Manager').exists() or 
            self.request.user.is_staff or self.request.user.is_superuser):
            return Cart.objects.all()

        return Cart.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        menuitem_id = request.data.get('menuitem')
        if not menuitem_id:
            return Response(
                {'error': 'menuitem is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response(
                {'error': 'Menu item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        existing_cart_item = Cart.objects.filter(
            user=request.user, 
            menuitem=menuitem
        ).first()
        
        if existing_cart_item:
            quantity = request.data.get('quantity', 1)
            existing_cart_item.quantity = quantity
            existing_cart_item.save()
            
            serializer = self.get_serializer(existing_cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if (request.user.groups.filter(name='Manager').exists() or 
            request.user.is_staff or request.user.is_superuser):
            Cart.objects.all().delete()
            return Response(
                {'message': 'All cart items deleted'}, 
                status=status.HTTP_200_OK
            )

        deleted_count = Cart.objects.filter(user=request.user).delete()[0]
        return Response(
            {'message': f'{deleted_count} cart items deleted'}, 
            status=status.HTTP_200_OK
        )

class ItemOfTheDayView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def get(self, request):
        item = MenuItem.objects.filter(featured=True).first()
        if item:
            serializer = MenuItemSerializer(item)
            return Response(serializer.data)
        return Response({"message": "No item of the day set."}, status=404)

    def post(self, request):
        if not request.user.is_authenticated or not (
            request.user.groups.filter(name="Manager").exists() or
            request.user.is_staff or request.user.is_superuser
        ):
            return Response({"detail": "Permission denied."}, status=403)

        menuitem_id = request.data.get('menuitem_id')
        if not menuitem_id:
            return Response({"error": "menuitem_id is required"}, status=400)

        try:
            menuitem = MenuItem.objects.get(pk=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found"}, status=404)

        MenuItem.objects.filter(featured=True).update(featured=False)

        menuitem.featured = True
        menuitem.save()

        return Response({"message": f"{menuitem.title} set as item of the day."})


class OrderListCreateView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=user)
        total = 0

        for item in cart_items:
            total += item.price
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        order.total = total
        order.save()
        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            return obj
        elif user.groups.filter(name='Delivery Crew').exists() and obj.delivery_crew == user:
            return obj
        else: 
            return obj
    

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        if user.groups.filter(name='Manager').exists():
            data = {}
            if 'delivery_crew' in request.data:
                data['delivery_crew'] = request.data['delivery_crew']
            if 'status' in request.data:
                data['status'] = request.data['status']
            serializer = self.get_serializer(order, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

        elif user.groups.filter(name='Delivery Crew').exists():
            if 'status' in request.data:
                order.status = request.data['status']
                order.save()
                return Response(self.get_serializer(order).data)
            else:
                return Response({'error': 'Only status can be updated'}, status=403)

        return Response({'error': 'Not allowed'}, status=403)


def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def menu(request):
    return render(request, 'menu.html')

def reservations(request):
    date = request.GET.get('date',datetime.today().date())
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html',{"bookings":booking_json})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

@csrf_exempt
def bookings(request):
    if request.method == "POST":
        data = json.load(request)
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(reservation_slot = data['reservation_slot']).exists()
        if exist == False:
            booking = Booking(first_name=data['first_name'], 
                              reservation_date=data['reservation_date'],
                              reservation_slot=data['reservation_slot'])
            booking.save()
        else:
            return HttpResponse("{'error':1}", content_type='application/json')
    date = request.GET.get('date', datetime.today().date())
    bookings = Booking.objects.all().filter(reservation_date=date)
    booking_json = serializers.serialize('json', bookings)
    return HttpResponse(booking_json, content_type='application/json')


# @api_view()
# @permission_classes([IsAuthenticated])
# def manager_view(request):
#     if request.user.groups.filter(name='Manager').exists():
#         return Response({"message": "Only Manager Should See This"})
#     else:
#         return Response({"message": "You are not authorized"}, 403)

