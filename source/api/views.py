import json

from django.core.serializers import serialize, deserialize
from django.http import HttpResponse, JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from webapp.models import Product


def product_list_view(request, *args, **kwargs):
    if request.method == 'GET':
        products = Product.objects.all()
        products_data = serialize('json', products)
        response = HttpResponse(products_data)
        response['Content-Type'] = 'application/json'
        return response


def product_list_view_v2(request, *args, **kwargs):
    if request.method == 'GET':
        fields = ('pk', 'name', 'category', 'photo', 'in_order', 'price')
        products = Product.objects.values(*fields)
        return JsonResponse(list(products), safe=False)


# Пример входных данных для product_create_view:
# [{
#   "model": "webapp.product",
#   "fields": {
#     "name": "Test",
#     "category": "food",
#     "price": "100.00"
#   }
# }]

@csrf_exempt
def product_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        if request.body:
            product_data = deserialize('json', request.body)
            for item in product_data:
                item.save()
                return JsonResponse({'id': item.object.pk})
        else:
            response = JsonResponse({'error': 'No data provided!'})
            response.status_code = 400
            return response


# Пример входных данных для product_create_view_v2:
# {
#   "name": "Test",
#   "category": "food",
#   "price": "100.00"
# }

@csrf_exempt
def product_create_view_v2(request, *args, **kwargs):
    if request.method == 'POST':
        if request.body:
            product_data = json.loads(request.body)
            product = Product.objects.create(**product_data)
            return JsonResponse({'id': product.pk})
        else:
            response = JsonResponse({'error': 'No data provided!'})
            response.status_code = 400
            return response