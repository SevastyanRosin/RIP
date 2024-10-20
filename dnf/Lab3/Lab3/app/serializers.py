from rest_framework import serializers

from .models import *


class UnitSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, unit):
        return unit.image.url.replace("minio", "localhost", 1)

    class Meta:
        model = Unit
        fields = "__all__"


class UnitItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_image(self, unit):
        return unit.image.url.replace("minio", "localhost", 1)

    def get_value(self, unit):
        return self.context.get("value")

    class Meta:
        model = Unit
        fields = ("id", "name", "image", "value")


class OrderSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, order):
        return order.owner.username

    def get_moderator(self, order):
        if order.moderator:
            return order.moderator.username
            
    def get_units(self, order):
        items = UnitOrder.objects.filter(order=order)
        return [UnitItemSerializer(item.unit, context={"value": item.value}).data for item in items]

    class Meta:
        model = Order
        fields = '__all__'


class OrdersSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, order):
        return order.owner.username

    def get_moderator(self, order):
        if order.moderator:
            return order.moderator.username

    class Meta:
        model = Order
        fields = "__all__"


class UnitOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOrder
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
