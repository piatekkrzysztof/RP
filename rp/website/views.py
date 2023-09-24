from datetime import datetime

from django.utils import timezone

from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializer import *


class TierViewSet(viewsets.ModelViewSet):
    queryset = Tier.objects.all()
    serializer_class = TierSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Image.objects.filter(user_id=user).exclude(photo__isnull=True)
        print("Queryset:", queryset)
        for obj in queryset:
            print("Object ID:", obj.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpLinkViewSet(viewsets.ModelViewSet):
    serializer_class = ExpLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.tier.allow_links:
            raise PermissionDenied("You don't have permission to create expiring links")
        return ExpLink.objects.filter(image__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.tier.allow_links:
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to create expiring links.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if datetime.now() > instance.expires_at:
            return Response({"message": "Link has expired"}, status=status.HTTP_410_GONE)
        else:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
