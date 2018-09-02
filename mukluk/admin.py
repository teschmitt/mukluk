from copy import deepcopy

from django.contrib import admin
from django.db.models import ImageField

from mezzanine.core.admin import DisplayableAdmin, TabularDynamicInlineAdmin

from cartridge.shop.admin import ProductAdmin
from cartridge.shop.forms import ImageWidget
from cartridge.shop.models import Product

from mukluk.models import (
    VendorShop, DesignedProduct, DesignAsset, Brand, DesignAsset)


shop_extra_fieldsets = ((None, {"fields": ("vendor", "content")}),)

product_fieldsets = deepcopy(ProductAdmin.fieldsets)
product_fieldsets[0][1]["fields"].insert(1, "brand")

designed_product_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
designed_product_fieldsets[0][1]["fields"].extend(
    ['base', 'vendor_shop', 'markup', 'content'])


class DesignAssetAdmin(TabularDynamicInlineAdmin):
    model = DesignAsset
    formfield_overrides = {ImageField: {"widget": ImageWidget}}


class VendorShopAdmin(DisplayableAdmin):
    fieldsets = deepcopy(DisplayableAdmin.fieldsets) + shop_extra_fieldsets


class DesignedProductAdmin(DisplayableAdmin):
    inlines = (DesignAssetAdmin,)
    fieldsets = designed_product_fieldsets


class MuklukProductAdmin(ProductAdmin):
    fieldsets = product_fieldsets

# class DesignAssetAdmin(TabularDynamicInlineAdmin):
#     model = DesignAsset
#     formfield_overrides = {ImageField: {"widget": ImageWidget}}


admin.site.unregister(Product)
admin.site.register(Product, MuklukProductAdmin)
admin.site.register(VendorShop, VendorShopAdmin)
# admin.site.register(InventoryProduct)
admin.site.register(Brand)
# admin.site.register(DesignAsset, DesignAssetAdmin)
admin.site.register(DesignedProduct, DesignedProductAdmin)
