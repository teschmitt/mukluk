from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from mezzanine.core.fields import FileField
from mezzanine.core.models import (
    TimeStamped, MetaData, Displayable, ContentTyped, Orderable)
from mezzanine.pages.models import RichText
from mezzanine.utils.models import upload_to

from cartridge.shop.models import Product, Priced
from cartridge.shop.fields import MoneyField, SKUField


class Profile(TimeStamped):
    user = models.OneToOneField("auth.User")
    date_of_birth = models.DateField(null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        app_label = "mukluk"


class Brand(Displayable, RichText):

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        app_label = "mukluk"


class VendorShop(RichText, Displayable):

    """
    Vendor shops for designed products
    """

    vendor = models.ForeignKey(
        Profile, related_name="vendor_shops", on_delete=models.CASCADE)

    def get_absolute_url(self):
        slug = self.slug
        return reverse("shop_content", kwargs={"shop_slug": slug})

    class Meta:
        verbose_name = _("Vendor Shop")
        verbose_name_plural = _("Vendor Shops")
        app_label = "mukluk"


class DesignedProduct(Displayable, RichText, ContentTyped):
    """
    Bringing together the Inventory and Designs to create a user designed product
    """

    base = models.ForeignKey(
        Product, related_name="designed_products", on_delete=models.CASCADE)
    vendor_shop = models.ForeignKey(
        VendorShop, related_name="designed_products", on_delete=models.CASCADE)
    markup = MoneyField(_('Markup'))
    sku = SKUField(blank=True, null=True)

    def price(self):
        return self.base.price() + self.markup

    def get_absolute_url(self):
        product_slug = self.slug
        shop_slug = self.vendor_shop.slug
        return reverse("designed_product", kwargs={
            "shop_slug": shop_slug,
            "product_slug": product_slug})

    class Meta:
        verbose_name = _("Designed Product")
        verbose_name_plural = _("Designed Products")
        app_label = "mukluk"

    def save(self, *args, **kwargs):
        self.set_content_model()
        super().save(*args, **kwargs)


class DesignedProductImage(Orderable):
    """
    An image for a DesignedProduct. Heavily borrows from the
    core ProductImage model.DesignedProduct
    """
    file = FileField(
        _("Image"), max_length=255, format="Image",
        upload_to=upload_to("shop.DeisgnedProductImage.file", "product"))
    description = models.CharField(_("Description"), blank=True, max_length=100)
    designed_product = models.ForeignKey(DesignedProduct, related_name="images")

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        order_with_respect_to = "designed_product"

    def __str__(self):
        value = self.description or self.file.name or ""
        return value


class DesignAsset(TimeStamped, MetaData):

    """
    An asset used to design a DesignedProduct.
    Right now, all positioning is included in the asset model. This might
    be broken out into a designated model (AssetComposition or something)
    in the future.

    Still missing:
      - Positioning information
    """
    designed_product = models.ForeignKey(
        DesignedProduct, related_name="design_assets", on_delete=models.CASCADE)
    file = FileField(
        _("Asset"), max_length=255, format="Image",
        upload_to=upload_to("shop.DesignAsset.file", "asset"))

    class Meta:
        verbose_name = _("Design Asset")
        verbose_name_plural = _("Design Assets")
        app_label = "mukluk"


# class ProductLink(TimeStamped):
#     inventory_product = models.ForeignKey(
#         InventoryProduct, related_name="link_inventory", on_delete=models.CASCADE)
#     vendor_product = models.ForeignKey(
#         Product, related_name="link_vendor", on_delete=models.CASCADE)
#     vendor_shop = models.ForeignKey(
#         VendorShop, related_name="prouct_link", on_delete=models.CASCADE)
#     design_asset = models.ForeignKey(
#         DesignAsset, related_name="product_link", on_delete=models.CASCADE)
#     markup = MoneyField(_("Markup"))

#     def vendor_shop_products(self, slug):
#         self.objects.filter(vendorshop__slug=slug)