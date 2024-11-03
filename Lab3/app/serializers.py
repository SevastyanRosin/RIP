from rest_framework import serializers

from .models import *


class UnitsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, unit):
        if unit.image:
            return unit.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Unit
        fields = ("id", "name", "status", "phone", "image")


class UnitSerializer(UnitsSerializer):
    class Meta(UnitsSerializer.Meta):
        model = Unit
        fields = UnitsSerializer.Meta.fields + ("description", )


class OrdersSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderSerializer(OrdersSerializer):
    units = serializers.SerializerMethodField()
            
    def get_units(self, order):
        items = UnitOrder.objects.filter(order=order)
        return [UnitItemSerializer(item.unit, context={"value": item.value}).data for item in items]


class UnitItemSerializer(UnitSerializer):
    value = serializers.SerializerMethodField()

    def get_value(self, unit):
        return self.context.get("value")

    class Meta(UnitSerializer.Meta):
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
