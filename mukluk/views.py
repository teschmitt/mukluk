from django.views.generic import ListView, DetailView

from mukluk.models import VendorShop, DesignedProduct


class ShopList(ListView):
    model = VendorShop


class ShopContent(ListView):
    model = DesignedProduct
    template_name = 'mukluk/usershopcontent_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('shop_slug', None)
        return DesignedProduct.objects.filter(vendor_shop__slug=slug)


class DesignedProductDetail(DetailView):
    model = DesignedProduct
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    # def get_queryset(self):
    #     shop_slug = self.kwargs.get('shop_slug', None)
    #     product_slug = self.kwargs.get('product_slug', None)
    #     return DesignedProduct.objects.filter(slug=product_slug)
