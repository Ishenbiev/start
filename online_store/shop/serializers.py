from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user':{
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_tocen),
            'refresh': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_tocen),
            'refresh': str(refresh),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ['image']


class RatingSerializer(serializers.ModelSerializer):
    user = UserProfileSimpleSerializer()

    class Meta:
        model = Rating
        fields = ['user', 'stars']


class ReviewSerializer(serializers.ModelSerializer):
    author = UserProfileSimpleSerializer()
    created_date = serializers.DateTimeField('%d-%m-%y  %H:%M')

    class Meta:
        model = Review
        fields = ['author', 'text', 'parent_review', 'created_date']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product = ProductPhotosSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product', 'category', 'price', 'date']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    ratings = RatingSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    product = ProductPhotosSerializer(read_only=True, many=True)
    date = serializers.DateField('%d-%m-%y')
    average_rating = serializers.SerializerMethodField()
    owner = UserProfileSimpleSerializer()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'description', 'product', 'product_video',
                  'price', 'active', 'average_rating', 'date', 'ratings', 'reviews', 'owner']

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')


    class Meta:
        model = CarItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']


    def get_total_price(self, obj):
        return obj.get_total_price()





