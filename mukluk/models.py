from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from django.core.urlresolvers import reverse

from mezzanine.core.fields import FileField
from mezzanine.core.models import (
    TimeStamped, MetaData, Displayable, ContentTyped, Orderable)
from mezzanine.pages.models import RichText
from mezzanine.utils.models import upload_to

from cartridge.shop.models import Product, Priced, Cart
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

    class Meta:
        verbose_name = _("Designed Product")
        verbose_name_plural = _("Designed Products")
        app_label = "mukluk"

    def __str__(self):
        return self.title

    @property
    def image(self):
        """
        Return the first image associated with the DesignedProduct
        """
        try:
            return DesignedProductImage.objects.filter(
                designed_product=self)[0] or None
        except IndexError:
            # Designed Product has no images
            return None

    def price(self):
        return self.base.price() + self.markup

    def get_absolute_url(self):
        product_slug = self.slug
        shop_slug = self.vendor_shop.slug
        return reverse("designed_product", kwargs={
            "shop_slug": shop_slug,
            "product_slug": product_slug})

    def save(self, *args, **kwargs):
        self.set_content_model()
        super().save(*args, **kwargs)
        if not self.sku:
            self.sku = self.id
            self.save()


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


# MONKEY PATCHES OF CORE MODELS
# -----------------------------
# Most of the Cartridge core is flexible enough to allow bending the
# system into a marketplace platform. Some of the core isn't, so
# this is where all the needed monkey patches for the Cartridge models
# reside.

def mukluk_add_item(self, variation, designed_product, quantity):
        """
        Modifies the Cartidge's Cart model to enable it to add
        DesignedProducts to the Cart.
        """
        if not self.pk:
            self.save()
        kwargs = {
            "sku": '{}-{}'.format(variation.sku, designed_product.sku),
            "unit_price": variation.price() + designed_product.markup}
        item, created = self.items.get_or_create(**kwargs)
        if created:
            item.description = '{} ({})'.format(
                force_text(designed_product), force_text(variation))
            item.unit_price = variation.price() + designed_product.markup
            item.url = designed_product.get_absolute_url()
            image = designed_product.image
            if image is not None:
                item.image = force_text(image.file)
            variation.product.actions.added_to_cart()
        item.quantity += quantity
        item.save()

Cart.add_item = mukluk_add_item
