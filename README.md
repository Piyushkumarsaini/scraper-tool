# Flipkart Scraper Tool (Django)

This is a Django-based backend project for scraping product data from **Flipkart**.  
It fetches product details such as name, price, offers, ratings, reviews, seller info, specifications, images, Q&A, and more.  
The data is stored in the database using Django models and can also be returned as JSON via an API endpoint.

---

## 🚀 Features

- Scrapes product details from Flipkart:
  - Name, Price, MRP, Offers
  - Coupons & Bank Offers
  - Delivery details
  - Seller info
  - RAM, Color, Storage, Purchase options
  - Ratings & Review blocks (with distribution + feature-wise ratings)
  - Product specifications
  - Product description (with images)
  - Q&A section
  - Product images
- Saves scraped data into the database (`Product` model).
- Provides JSON API endpoint for scraping.

---

## 📂 Project Structure

