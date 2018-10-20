from django.db.models import Manager

class DesignedProductManager(Manager):

    def create_from_bases(self, bases):
        """
        Create all DesignedProducts from the selected base Products
        and the used Design.
        """
        if bases:
            for b in bases:
                print("ADDING BASE {}, type {}".format(b, type(b)))
