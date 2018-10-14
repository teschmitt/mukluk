from copy import deepcopy

from django.contrib.admin import TabularInline, site
from django.db.models import ImageField
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from mezzanine.core.admin import (
    DisplayableAdmin, TabularDynamicInlineAdmin)

from cartridge.shop.admin import ProductAdmin
from cartridge.shop.forms import ImageWidget
from cartridge.shop.models import Product

from mukluk.forms import DesignAdminForm
from mukluk.models import (
    VendorShop, Design, DesignAsset, Brand,
    DesignedProductImage, DesignedProduct)


shop_extra_fieldsets = ((None, {"fields": ("vendor", "content")}),)

product_fieldsets = deepcopy(ProductAdmin.fieldsets)
product_fieldsets[0][1]["fields"].insert(1, "brand")

# designed_product_fields = [force_text(p) for p in Product.objects.all()]
design_fieldsets = list(deepcopy(DisplayableAdmin.fieldsets))
design_fieldsets[0][1]["fields"].extend(['content'])
design_fieldsets.insert(50, (
    _("Select Products available with this Design"),
    {"classes": ("create-designedproducts",), "fields": ["base"]}))


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
    inlines = (DesignAssetAdmin,)
    form = DesignAdminForm
    fieldsets = design_fieldsets


site.unregister(Product)
site.register(Product, MuklukProductAdmin)
site.register(VendorShop, VendorShopAdmin)
# admin.site.register(InventoryProduct)
site.register(Brand)
# admin.site.register(DesignAsset, DesignAssetAdmin)
site.register(Design, DesignAdmin)
