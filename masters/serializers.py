from rest_framework import serializers
from .models import *

class amenity_serializer(serializers.ModelSerializer):
    class Meta:
        model = amenity
        fields = '__all__'

class property_type_serializer(serializers.ModelSerializer):
    class Meta:
        model = property_type
        fields = '__all__'

class city_serializer(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = '__all__'

class villa_amenity_serializer(serializers.ModelSerializer):
    class Meta:
        model = villa_amenity
        fields = '__all__'

class villa_type_serializer(serializers.ModelSerializer):
    class Meta:
        model = villa_type
        fields = '__all__'


class coupon_serializer(serializers.ModelSerializer):
    class Meta:
        model = coupon
        fields = '__all__'


class customer_address_serializer(serializers.ModelSerializer):
    
    class Meta:
        model = customer_address
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        # Inject authenticated user manually
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

    
class testimonials_serializer(serializers.ModelSerializer):
    class Meta:
        model = testimonials
        fields = '__all__'



class event_serializer(serializers.ModelSerializer):
    class Meta:
        model = event
        fields = '__all__'




# Step 1: Create a serializer
class HomeBannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = home_banner
        fields = ['id', 'title', 'description', 'image', 'category', 'is_for_web', 'is_active', 'created_at']
    
    def get_image(self, obj):
        """
        Return absolute URL for banner image.
        """
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None