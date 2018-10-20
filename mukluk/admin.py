from copy import deepcopy

from django.contrib.admin import TabularInline, site
from django.db.models import ImageField
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from mezzanine.core.admin import (
    DisplayableAdmin, TabularDynamicInlineAdmin)

from cartridge.shop.admin import ProductAdmin
from cartridge.shop.fields import MoneyField
from cartridge.shop.forms import ImageWidget, MoneyWidget
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
design_fieldsets[0][1]["fields"].extend(['content', 'vendor_shop'])
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
    verbose_name_plural = _("Current Designed Products")
    model = DesignedProduct
    fields = ['base', 'sku', 'markup']
    max_num = None
    extra = 0
    formfield_overrides = {MoneyField: {"widget": MoneyWidget}}


class MuklukProductAdmin(ProductAdmin):
    fieldsets = product_fieldsets


class DesignAdmin(DisplayableAdmin):
    """
    This admin uses a similiar aproach as Cartridge's
    ProductAdmin class. A selection of possible Products
    is displayed. When selected, DesignedProducts of the selected
    Products are created.
    """

    inlines = (DesignAssetAdmin, DesignedProductAdmin)
    form = DesignAdminForm
    fieldsets = design_fieldsets

    def save_model(self, request, obj, form, change):
        """
        Store the design ID for creating designed_products
        in save_formset.
        """
        super(DesignAdmin, self).save_model(request, obj, form, change)
        self._design_id = obj.id

    def save_formset(self, request, form, formset, change):
        design = self.model.objects.get(id=self._design_id)
        print('Running trough {}'.format(formset.model))
        # if formset.model == DesignAsset:
        #     super(DesignAdmin, self).save_formset(request, form, formset,
        #                                           change)
        if formset.model == DesignedProduct:
            bases = request.POST.getlist('base')
            design.designed_products.create_from_bases(bases)

site.unregister(Product)
site.register(Product, MuklukProductAdmin)
site.register(VendorShop, VendorShopAdmin)
site.register(Brand)
site.register(Design, DesignAdmin)
