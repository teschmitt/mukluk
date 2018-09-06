==============================================
Overrides of the Cartridge and Mezzanine Core
==============================================

Mukluk is based on `Cartridge <http://cartridge.jupo.org>`_, a shopping cart application built using the Django framework and extending the `Mezzanine <http://mezzanine.jupo.org/>`_ CMS. As such, some workarounds had to be put in place to support a multi-vendor marketplace solution.

Following are some notes on the various overrides of the core Cartridge and Mezzanine codebase and how they are performed.


SKUs
====

A lot of cart and order functionality relies on the SKUs that each reference a certain :class:`.ProductVariant`. A :class:`.DesignedProduct` is based on a :class:`.Product`, but orders are of a certain variant of that product that is then used for printing on the design.

o easily identify the ordered design as well as the base product unto which it should be printed, modified SKUs are generated and have two parts to them:

    1. SKU of the :class:`.ProductVariant`

followed by a minus/hyphen (`-`) and then part

    2. SKU of the :class:`.DesignedProduct`

Modifying the SKUs in this ways screws up some of Cartridge's core that is responsible for filtering cart or order items based on the SKU. These workarounds take care of maintaining regular functionality:

    * :mod:`.mukluk.models`
        .. autofunction:: mukluk.models.mukluk_add_item
            :noindex:

        Replaces core :meth:`.Cart.add_item`

        Todo: Instead of monkey-patching, we could also create a custom object passed to the core add_item()-method that includes all desired information. This seems to be the more future-proof solution.

    * :mod:`.mukluk.views`
        .. autofunction:: mukluk.views.mukluk_complete
            :noindex:

        Gets called as a replacement for the core view :func:`complete`

Designed Products
=================

    * :mod:`.mukluk.views`
        .. autofunction:: mukluk.views.designed_product
            :noindex:

        Gets called to display the product page for a :class:`.DesignedProduct`

        The only real changes are in the function definition (``product_slug`` and ``shop_slug`` parameters) and right in the beginning, where the DesignedProduct has to be fetched as well for further processing (cart, order, etc):

        .. literalinclude:: ../../../mukluk/views.py
           :pyobject: designed_product
           :linenos:
           :emphasize-lines: 1,2,4-6,9,20,27,46,47,49,58,61
