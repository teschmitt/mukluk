from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from mezzanine.core.fields import FileField
from mezzanine.core.models import Ownable, TimeStamped, MetaData, Displayable
from mezzanine.pages.models import RichText, Page
from mezzanine.utils.models import upload_to

from cartridge.shop.models import Product, BaseProduct, Priced
from cartridge.shop.fields import MoneyField


class Profile(TimeStamped):
    user = models.OneToOneField("auth.User")
    date_of_birth = models.DateField(null=True)


class DesignAsset(TimeStamped, MetaData):

    """
    An asset used to design a DesignedProduct.
    Right now, all positioning is included in the asset model. This might
    be broken out into a designated model (AssetComposition or something)
    in the future.

    Still missing:
      - Positioning information
    """
    vendor = models.ForeignKey(
        Profile, related_name="design_assets", on_delete=models.CASCADE)
    file = FileField(
        _("Asset"), max_length=255, format="Asset File",
        upload_to=upload_to("shop.DesignAsset.file", "asset"))

    class Meta:
        verbose_name = _("Design Asset")
        verbose_name_plural = _("Design Assets")
        app_label = "mukluk"


class Brand(Displayable, RichText):

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        app_label = "mukluk"


class InventoryProduct(BaseProduct, Priced, RichText):

    """
    Model for inventory products
    Includes a markup on the product price.

    Missing:
      - Number of colors used in the design
    """

    price = MoneyField

    class Meta:
        verbose_name = _("Inventory Product")
        verbose_name_plural = _("Inventory Products")
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
