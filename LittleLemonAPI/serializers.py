from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'inventory', 'featured', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 2},
            'inventory': {'min_value': 0},
            'title': {'validators': [UniqueValidator(queryset=MenuItem.objects.all())]}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menuitem_title', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']
    
    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        validated_data['unit_price'] = menuitem.price
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'menuitem_title', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['user', 'total', 'date', 'order_items']