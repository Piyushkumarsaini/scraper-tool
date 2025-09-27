from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    extra_off = models.CharField(max_length=255, blank=True, null=True)
    price = models.CharField(max_length=50, blank=True, null=True)
    mrp = models.CharField(max_length=50, blank=True, null=True)
    offer = models.CharField(max_length=255, blank=True, null=True)

    # Use JSONField for lists/dicts
    protect_info = models.JSONField(blank=True, null=True)
    ratings_reviews = models.JSONField(blank=True, null=True)
    coupons = models.JSONField(blank=True, null=True)
    bank_offers = models.JSONField(blank=True, null=True)
    purchase_options = models.JSONField(blank=True, null=True)
    color_options = models.JSONField(blank=True, null=True)
    storage_options = models.JSONField(blank=True, null=True)
    ram_options = models.JSONField(blank=True, null=True)

    delivery_date = models.CharField(max_length=100, blank=True, null=True)
    delivery_note = models.TextField(blank=True, null=True)
    payment_offers = models.JSONField(blank=True, null=True)
    seller_info = models.JSONField(blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    specifications = models.JSONField(blank=True, null=True)
    question_answer = models.JSONField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    product_url = models.URLField(blank=True, null=True)
