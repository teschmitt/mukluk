from copy import deepcopy

from django.contrib import admin
from mezzanine.core.admin import DisplayableAdmin
from mukluk.models import UserShop, DesignedProduct, DesignAsset

shop_extra_fieldsets = ((None, {"fields": ("user", "products", "content",)}),)

# print(DisplayableAdmin.fieldsets)


class UserShopAdmin(DisplayableAdmin):
    fieldsets = deepcopy(DisplayableAdmin.fieldsets) + shop_extra_fieldsets


admin.site.register(UserShop, UserShopAdmin)
admin.site.register(DesignedProduct)
admin.site.register(DesignAsset)
