from django.db import models
from django.db import models
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=100, null=True, blank=True)
    mrp = models.CharField(max_length=100, null=True, blank=True)
    offer = models.CharField(max_length=255, null=True, blank=True)
    ratings_reviews = models.CharField(max_length=100, null=True, blank=True)
    delivery_date = models.CharField(max_length=100, null=True, blank=True)
    delivery_note = models.TextField(null=True, blank=True)
    bank_offers = models.TextField(null=True, blank=True)
    payment_offers = models.TextField(null=True, blank=True)
    ram_options = models.JSONField(null=True, blank=True)  # assuming list or dict
    color_options = models.JSONField(null=True, blank=True)
    purchase_options = models.JSONField(null=True, blank=True)
    product_description = models.JSONField(null=True, blank=True)
    specifications = models.JSONField(null=True, blank=True)
    question_answer = models.JSONField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    product_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name
