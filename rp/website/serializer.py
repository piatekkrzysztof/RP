import logging
import os

from PIL import Image as PILImage
from django.conf import settings
from rest_framework import serializers

from .models import *

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ExpLinkSerializer(serializers.HyperlinkedModelSerializer):
    expires_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = ExpLink
        fields = ['image', 'duration', 'photo_url', 'expires_at']

    def __init__(self, *args, **kwargs):
        super(ExpLinkSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            self.fields['image'].queryset = Image.objects.filter(user=request.user)

    def validate(self, data):
        user = self.context['request'].user
        if not user.tier.allow_links:
            raise serializers.ValidationError("You don't have permission to create expiring links.")
        return data

    def validate_duration(self, value):
        total_seconds = value.total_seconds()
        if total_seconds < 300 or total_seconds > 30000:
            raise serializers.ValidationError("Duration MUST be between 300 and 30000!")
        return value

    def validate_image(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("You can't create a link for an image that doesn't belong to you.")
        return value

    def get_photo_url(self, obj):
        if timezone.now() > obj.expires_at:
            obj.delete()
            return "Link has expired and the object has been deleted"
        request = self.context.get('request')
        photo_url = obj.image.photo.url
        return request.build_absolute_uri(photo_url)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('duration')
        ret.pop('image')
        return ret


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'tier']


class TierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tier
        fields = ['name', 'thumbnail_s_height', 'thumbnail_m_height', 'orginal_link', 'allow_links']

    def validate_thumbnail_s_height(self, value):
        if value < 1 or value > 1920:
            raise serializers.ValidationError("Thumbnail height can't be lower than 1px or higher than 1920px.")
        return value

    def validate_thumbnail_m_height(self, value):
        if value < 1 or value > 1920:
            raise serializers.ValidationError("Thumbnail height can't be lower than 1px or higher than 1920px.")
        return value


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ['id','date', 'photo']

    def create_thumbnail(self, obj, size):
        pil_image = PILImage.open(obj.photo)
        base_width, base_height = pil_image.size
        if len(size) == 1:
            height = size[0]
            width = int((height / base_height) * base_width)
            size = (width, height)
        pil_image.thumbnail(size)
        thumb_name = f"{size[0]}x{size[1]}_{obj.photo.name.split('/')[-1]}"
        thumb_path = os.path.join(settings.MEDIA_ROOT, 'upimages', thumb_name)
        pil_image.save(thumb_path, 'PNG')
        request = self.context.get('request')
        thumb_url = f"{settings.MEDIA_URL}upimages/{thumb_name}"
        return request.build_absolute_uri(thumb_url)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user = self.context['request'].user

        logger.info(f"Generating thumbnails for user {user.id} with tier {user.tier}")

        ret['thumbnail_s'] = self.create_thumbnail(instance, (user.tier.thumbnail_s_height,))
        if user.tier.thumbnail_m_height != 0:
            ret['thumbnail_m'] = self.create_thumbnail(instance, (user.tier.thumbnail_m_height,))
        if not user.tier.orginal_link:
            ret.pop('photo', None)
        return ret
