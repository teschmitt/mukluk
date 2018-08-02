from django.views.generic import ListView, DetailView

from mukluk.models import UserShop, DesignedProduct


class ShopList(ListView):
    model = UserShop


class ShopContent(ListView):
    model = DesignedProduct
    template_name = 'mukluk/usershopcontent_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('shop_slug', None)
        return DesignedProduct.objects.filter(usershop__slug=slug)


class DesignedProductDetail(DetailView):
    model = DesignedProduct
