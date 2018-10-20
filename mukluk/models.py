from django.db.models import (
    ForeignKey, ManyToManyField, CharField, DateField,
    OneToOneField, CASCADE)
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

from mukluk import managers


class Profile(TimeStamped):
    user = OneToOneField("auth.User")
    date_of_birth = DateField(null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class Brand(Displayable, RichText):

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")


class VendorShop(RichText, Displayable):

    """
    Vendor shops for designed products
    """

    vendor = ForeignKey(
        Profile, related_name="vendor_shops", on_delete=CASCADE)

    def get_absolute_url(self):
        slug = self.slug
        return reverse("shop_content", kwargs={"shop_slug": slug})

    class Meta:
        verbose_name = _("Vendor Shop")
        verbose_name_plural = _("Vendor Shops")


class DesignedProduct(TimeStamped):
    """
    This Through-Model stores the relationship of user submitted Designs
    and available Inventory Products. Every combination of Design and Product
    is represented in one record.user

    Additionally, we store all possible custom product configuration in here:
        - Markup: Amount the seller earns when DesignedProduct is sold
        - SKU: Unique identifier of DesignedProduct
        - AssetPlacement: TODO Infos on how DesignAssets are arranged/placed
    """

    design = ForeignKey(
        'Design', on_delete=CASCADE, related_name='designed_products')
    base = ForeignKey(Product, on_delete=CASCADE)
    markup = MoneyField(_('Markup'))
    sku = SKUField(blank=True, null=True)

    objects = managers.DesignedProductManager()

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

    def unit_price(self):
        return self.base.unit_price() + self.markup

    def price(self):
        return self.base.price() + self.markup

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.sku:
            self.sku = self.id
            self.save()


class Design(Displayable, RichText):
    """
    Central model for mukluk! Every user created Design is wired to all other
    parts of the mukluk system here.
    This model links DesignAssets to DesignAssets, possible base Products, and
    VendorShops. DesignedProduct stores all possible custom product
    configurability.
    """

    possible_products = ManyToManyField(
        Product, related_name='designs',
        through=DesignedProduct, through_fields=('design', 'base'))
    vendor_shop = ForeignKey(
        VendorShop, related_name="designs", on_delete=CASCADE)

    def get_absolute_url(self):
        design_slug = self.slug
        shop_slug = self.vendor_shop.slug
        return reverse("design", kwargs={
            "design_slug": design_slug,
            "shop_slug": shop_slug})

    class Meta:
        verbose_name = _("Design")
        verbose_name_plural = _("Designs")

    def __str__(self):
        return self.title


class DesignAsset(TimeStamped, MetaData):

    """
    An asset used to design a DesignedProduct.
    Right now, all positioning is included in the asset model. This might
    be broken out into a designated model (AssetComposition or something)
    in the future.

    Still missing:
      - Positioning information
    """
    design = ForeignKey(
        Design, related_name="design_assets", on_delete=CASCADE)
    file = FileField(
        _("Asset"), max_length=255, format="Image",
        upload_to=upload_to("shop.DesignAsset.file", "asset"))

    class Meta:
        verbose_name = _("Design Asset")
        verbose_name_plural = _("Design Assets")


class DesignedProductImage(Orderable):
    """
    An image for a DesignedProduct. Heavily borrows from the
    core ProductImage model.DesignedProduct
    """

    designed_product = ForeignKey(DesignedProduct, related_name="images")
    file = FileField(
        _("Image"), max_length=255, format="Image",
        upload_to=upload_to("shop.DeisgnedProductImage.file", "product"))
    # description = CharField(_("Description"), blank=True, max_length=100)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        order_with_respect_to = "designed_product"

    def __str__(self):
        value = self.description or self.file.name or ""
        return value


# MONKEY PATCHES OF CORE MODELS
# -----------------------------
# Most of the Cartridge core is flexible enough to allow bending the
# system into a marketplace platform. Some of the core isn't, so
# this is where all the needed monkey patches for the Cartridge models
# reside.
#
# Todo: Instead of monkey-patching, we could also create a custom
# object passed to the core add_item-method that includes all desired
# information. This seems to be the more future-proof solution.

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
