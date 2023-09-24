from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User, Tier


@admin.register(User)
class AddUserAdmin(admin.ModelAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tier',)}),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('tier',)}),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Tier)
class AddTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'thumbnail_s_height', 'thumbnail_m_height', 'orginal_link', 'allow_links']


admin.site.unregister(Group)
