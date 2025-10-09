from django.shortcuts import render

# Create your views here.
def homepage(request):
    return render(request, 'index.html')

def products(request):
    return render(request, 'products.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def product_details(request):
    return render(request, 'product-details.html')