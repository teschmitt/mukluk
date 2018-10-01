from copy import deepcopy

from django.contrib.admin import ModelAdmin, TabularInline, site
from django.db.models import ImageField

from mezzanine.core.admin import (
    DisplayableAdmin, TabularDynamicInlineAdmin)

from cartridge.shop.admin import ProductAdmin
from cartridge.shop.forms import ImageWidget
from cartridge.shop.models import Product

from mukluk.models import (
    VendorShop, Design, DesignAsset, Brand, DesignAsset,
    DesignedProductImage, DesignedProduct)


shop_extra_fieldsets = ((None, {"fields": ("vendor", "content")}),)

product_fieldsets = deepcopy(ProductAdmin.fieldsets)
product_fieldsets[0][1]["fields"].insert(1, "brand")

design_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
design_fieldsets[0][1]["fields"].extend(['content'])


class DesignAssetAdmin(TabularDynamicInlineAdmin):
    model = DesignAsset
    formfield_overrides = {ImageField: {"widget": ImageWidget}}


class DesignedProductImageAdmin(TabularDynamicInlineAdmin):
    model = DesignedProductImage
    formfield_overrides = {ImageField: {"widget": ImageWidget}}


class VendorShopAdmin(DisplayableAdmin):
    fieldsets = deepcopy(DisplayableAdmin.fieldsets) + shop_extra_fieldsets


class DesignedProductAdmin(TabularInline):
    model = DesignedProduct
    inlines = (DesignAssetAdmin,)


class MuklukProductAdmin(ProductAdmin):
    fieldsets = product_fieldsets


class DesignAdmin(DisplayableAdmin):
    inlines = (DesignAssetAdmin, DesignedProductAdmin,)
    fieldsets = design_fieldsets


# class DesignAssetAdmin(TabularDynamicInlineAdmin):
#     model = DesignAsset
#     formfield_overrides = {ImageField: {"widget": ImageWidget}}


site.unregister(Product)
site.register(Product, MuklukProductAdmin)
site.register(VendorShop, VendorShopAdmin)
# admin.site.register(InventoryProduct)
site.register(Brand)
# admin.site.register(DesignAsset, DesignAssetAdmin)
site.register(Design, DesignAdmin)
