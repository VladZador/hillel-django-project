import csv

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, RedirectView
from django.utils.translation import gettext_lazy as _

from orders.models import Order
from .models import Product


class ProductListView(ListView):
    model = Product


class ProductDetailView(DetailView):
    model = Product


@method_decorator(login_required, name='dispatch')
class AddToCartView(RedirectView):
    url = reverse_lazy("product_list")

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get_or_create(
                user=request.user,
                is_active=True
            )[0]
            product = Product.objects.get(pk=kwargs["pk"])
            order.products.add(product)
            order.save()
            return super().get(request, *args, **kwargs)
        except Product.DoesNotExist:
            raise Http404(_("Sorry, there is no product with this uuid"))


@login_required
def export_csv(request, *args, **kwargs):
    """Creates a csv file with products data from the database."""
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename="products.csv"'
        },
    )
    writer = _create_csv_writer(response)
    for product in Product.objects.iterator():
        _write_csv_row(writer, product)
    return response


@login_required
def export_csv_detail(request, *args, **kwargs):
    """
    Creates a csv file with data of the specified product from the database.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment;'
                                   f'filename="product-{kwargs["pk"]}.csv"'
        },
    )
    writer = _create_csv_writer(response)
    product = Product.objects.get(pk=kwargs["pk"])
    _write_csv_row(writer, product)
    return response


def _create_csv_writer(response):
    """Creates a csv writer object with the product info headers."""
    fieldnames = ["name", "description", "category", "price", "sku", "image"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    return writer


def _write_csv_row(writer, product_instance):
    """Adds parameters to be passed to the csv writer object."""
    writer.writerow(
        {
            "name": product_instance.name,
            "description": product_instance.description,
            "category": product_instance.category,
            "price": product_instance.price,
            "sku": product_instance.sku,
            "image": settings.DOMAIN + product_instance.image.url,
        }
    )
    return writer
