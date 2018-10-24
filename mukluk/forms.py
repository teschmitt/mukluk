from django import forms
from django.forms.models import ModelFormMetaclass

from cartridge.shop.models import Product
from cartridge.shop.utils import make_choices

from mukluk.models import Design


class DesignAdminFormMetaclass(ModelFormMetaclass):
    """

    """
    def __new__(cls, name, bases, attrs):
        field = forms.MultipleChoiceField(
            label="Base Product",
            required=False, widget=forms.CheckboxSelectMultiple)
        attrs["base"] = field
        args = (cls, name, bases, attrs)
        return super(DesignAdminFormMetaclass, cls).__new__(*args)


class DesignAdminForm(forms.ModelForm, metaclass=DesignAdminFormMetaclass):
    """
    Admin form for the Design model.
    """

    class Meta:
        model = Design
        exclude = []

    def __init__(self, *args, **kwargs):
        """

        """
        super(DesignAdminForm, self).__init__(*args, **kwargs)
        base_products = list((p['id'], p['title']) for p in Product.objects.values('id', 'title'))
        self.fields['base'].choices = base_products
