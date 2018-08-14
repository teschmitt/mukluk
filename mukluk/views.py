from django.views.generic import ListView, DetailView

from mukluk.models import VendorShop, InventoryProduct


class ShopList(ListView):
    model = VendorShop


class ShopContent(ListView):
    model = InventoryProduct
    template_name = 'mukluk/usershopcontent_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('shop_slug', None)
        return InventoryProduct.objects.filter(usershop__slug=slug)


class DesignedProductDetail(DetailView):
    model = InventoryProduct
