from json import dumps

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.template.response import TemplateResponse
from django.contrib.messages import info
from django.utils.translation import (ugettext, ugettext_lazy as _,
                                      pgettext_lazy as __)
from django.utils.encoding import force_text


from mezzanine.conf import settings

from cartridge.shop.utils import recalculate_cart
from cartridge.shop.forms import AddProductForm
from cartridge.shop.models import Product, ProductVariation

from mukluk.models import VendorShop, DesignedProduct


def modify_cart_desc(variation_str: None, designed_product: None):
    """
    This is going to return a function that replaces the __str__ method of the
    underlying ProductVariant of the DesignedProduct in order to modify
    the description of the item being added to the cart
    """
    return lambda: '{} -- {}'.format(designed_product, variation_str)


class ShopList(ListView):
    model = VendorShop


class ShopContent(ListView):
    model = DesignedProduct
    template_name = 'mukluk/usershopcontent_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('shop_slug', None)
        return DesignedProduct.objects.filter(vendor_shop__slug=slug)


def designed_product(request, product_slug, shop_slug,
                     template="mukluk/designed_product.html",
                     form_class=AddProductForm, extra_context=None):
    published_dps = DesignedProduct.objects.published(for_user=request.user)
    designed_product = get_object_or_404(published_dps, slug=product_slug)
    base = get_object_or_404(Product, slug=designed_product.base.slug)

    fields = [f.name for f in ProductVariation.option_fields()]
    variations = base.variations.all()
    variations_json = dumps([dict(
        [(f, getattr(v, f)) for f in fields + ["sku", "image_id"]])
        for v in variations])
    to_cart = (request.method == "POST" and
               request.POST.get("add_wishlist") is None)

    initial_data = {}
    if variations:
        initial_data = dict([(f, getattr(variations[0], f)) for f in fields])
    initial_data["quantity"] = 1
    add_product_form = form_class(request.POST or None, product=base,
                                  initial=initial_data, to_cart=to_cart)
    if request.method == "POST":
        if add_product_form.is_valid():
            if to_cart:
                quantity = add_product_form.cleaned_data["quantity"]
                request.cart.add_item(
                    add_product_form.variation, designed_product, quantity)
                recalculate_cart(request)
                info(request, _("Item added to cart"))
                return redirect("shop_cart")
            else:
                skus = request.wishlist
                sku = add_product_form.variation.sku
                if sku not in skus:
                    skus.append(sku)
                info(request, _("Item added to wishlist"))
                response = redirect("shop_wishlist")
                set_cookie(response, "wishlist", ",".join(skus))
                return response

    # related = []
    # if settings.SHOP_USE_RELATED_PRODUCTS:
    #     related = product.related_products.published(for_user=request.user)

    context = {
        "designed_product": designed_product,
        "product": base,
        "editable_obj": designed_product,
        "images": designed_product.images.all(),
        "variations": variations,
        "variations_json": variations_json,
        "has_available_variations": any([v.has_price() for v in variations]),
        # "related_products": related,
        "add_product_form": add_product_form
    }
    context.update(extra_context or {})

    templates = [u"mukluk/%s.html" % str(designed_product.slug), template]
    # Check for a template matching the page's content model.
    if getattr(designed_product, 'content_model', None) is not None:
        templates.insert(0, u"shop/products/%s.html" % designed_product.content_model)

    return TemplateResponse(request, templates, context)
