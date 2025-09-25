from django.urls import path
from .views import scrape_flipkart_json

urlpatterns = [
    path('scrape/', scrape_flipkart_json, name='scrape_flipkart_json'),
]
