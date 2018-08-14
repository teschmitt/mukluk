from copy import deepcopy

from django.contrib import admin
from django.db.models import ImageField

from mezzanine.core.admin import DisplayableAdmin, TabularDynamicInlineAdmin

from cartridge.shop.admin import ProductAdmin
from cartridge.shop.forms import DiscountAdminForm, ImageWidget, MoneyWidget
from cartridge.shop.models import Product

from mukluk.models import VendorShop, InventoryProduct, DesignAsset


shop_extra_fieldsets = ((None, {"fields": ("user", "products", "content",)}),)

product_fieldsets = deepcopy(ProductAdmin.fieldsets)
product_fieldsets[0][1]["fields"] += (
        "vendor", "vendor_shop", "markup", "inventory_product",)


class VendorShopAdmin(DisplayableAdmin):
    fieldsets = deepcopy(DisplayableAdmin.fieldsets) + shop_extra_fieldsets


class MuklukProductAdmin(ProductAdmin):
    fieldsets = product_fieldsets

# class DesignAssetAdmin(TabularDynamicInlineAdmin):
#     model = DesignAsset
#     formfield_overrides = {ImageField: {"widget": ImageWidget}}


admin.site.unregister(Product)
admin.site.register(Product, MuklukProductAdmin)
admin.site.register(VendorShop, VendorShopAdmin)
admin.site.register(InventoryProduct)
# admin.site.register(DesignAsset, DesignAssetAdmin)
