from django.db.models import Manager

from cartridge.shop.models import Product


class DesignedProductManager(Manager):

    def create_from_bases(self, design, bases):
        """
        Create all DesignedProducts from the selected base Products
        and the used Design.
            design: Design Instance
        """
        if bases:
            for base in map(int, bases):
                # Just add a DesignedProduct with base id b
                # to self
                # d = Design.objects.get(id=design)
                b = Product.objects.get(id=base)
                lookup = {'design': design, 'base': b}
                try:
                    self.get(**lookup)
                except self.model.DoesNotExist:
                    self.create(**lookup)
