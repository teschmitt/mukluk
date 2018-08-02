from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from mezzanine.core.fields import FileField
from mezzanine.core.models import Ownable, TimeStamped, MetaData, Displayable
from mezzanine.pages.models import RichText, Page
from mezzanine.utils.models import upload_to

from cartridge.shop.models import Product, BaseProduct
from cartridge.shop.fields import MoneyField


class DesignAsset(Ownable, TimeStamped, MetaData):

    """
    An asset used to design a DesignedProduct.
    Right now, all positioning is included in the asset model. This might
    be broken out into a designated model (AssetComposition or something)
    in the future.

    Still missing:
      - Positioning information
    """

    file = FileField(_("Asset"), max_length=255, format="Asset File",
        upload_to=upload_to("shop.DesignAsset.file", "asset"))

    class Meta:
        verbose_name = _("Design Asset")
        verbose_name_plural = _("Design Assets")
        app_label = "mukluk"


class DesignedProduct(Ownable, BaseProduct):

    """
    Model for user designed products
    Includes a markup on the product price.

    Missing:
      - Number of colors used in the design
    """

    product = models.ForeignKey(Product, related_name="designed_products")
    asset = models.ForeignKey(DesignAsset, related_name="designed_products")
    markup = MoneyField(_("Markup"))

    class Meta:
        verbose_name = _("Designed Product")
        verbose_name_plural = _("Designed Products")
        app_label = "mukluk"


class UserShop(RichText, Ownable, Displayable):

    """
    User shops for designed products
    """

    products = models.ManyToManyField(
        DesignedProduct, blank=True, verbose_name=_("Designed Products"))

    def get_absolute_url(self):
        slug = self.slug
        return reverse("shop_content", kwargs={"shop_slug": slug})

    class Meta:
        verbose_name = _("User Shop")
        verbose_name_plural = _("User Shops")
        app_label = "mukluk"
