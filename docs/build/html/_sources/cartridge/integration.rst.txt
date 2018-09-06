===========================
Cartridge Integration Hooks
===========================

Integration hooks are described in Cartidge's docs `here <http://cartridge.jupo.org/integration.html>`_. The mostimportant hooks can be routed in the following settings:

- SHOP_HANDLER_BILLING_SHIPPING = "cartridge.shop.checkout.default_billship_handler"
- SHOP_HANDLER_TAX = "cartridge.shop.checkout.default_tax_handler"
- SHOP_HANDLER_PAYMENT = "cartridge.shop.checkout.default_payment_handler"
- SHOP_HANDLER_ORDER = "cartridge.shop.checkout.default_order_handler"


Resources
=========

Tax / VAT
---------

- European style included VAT as a template tag: https://github.com/stephenmcd/cartridge/issues/234

- VAT injected into core models: https://groups.google.com/d/topic/mezzanine-users/9pcOT-tjSks/discussion

