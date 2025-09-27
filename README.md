# 🛒 Flipkart Scraper Tool (Django)

This is a Django-based backend project for scraping product data from **Flipkart**.  
It fetches product details such as name, price, offers, ratings, reviews, seller info, specifications, images, Q&A, and more.  
The data is stored in a database using Django models and returned as JSON via a RESTful API endpoint.

---

## 🚀 Features

- Scrapes product details from Flipkart:
  - Name, Price, MRP, Offers
  - Coupons & Bank Offers
  - Delivery details
  - Seller information
  - RAM, Color, Storage, and Purchase options
  - Ratings & Reviews (with distribution and feature-wise ratings)
  - Product specifications
  - Product descriptions (with images)
  - Q&A section
  - Product images
- Saves scraped data into a database (`Product` model).
- Provides a JSON API endpoint (`/scrape/`) for retrieving scraped data.

---

## 📂 Project Structure

- **views.py** → Scraping logic, including `scrape_flipkart_json` view and helpers (`scrape_product_details`, `extract_product_urls`).
- **models.py** → Defines the `Product` model with fields for storing scraped data.
- **urls.py** → Configures the `/scrape/` endpoint.
- **requirements.txt** → Required Python packages (`requests`, `beautifulsoup4`, `django`).
- **manage.py** → Django’s command-line utility.

---

## 🛠 Requirements

- Python 3.9+  
- Django 4.x+  
- SQLite (default) or another Django-supported database  
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `django`

---

## ⚙️ Setup

Clone the repository:

```bash
git clone https://github.com/Piyushkumarsaini/scraper-tool.git
cd scraper-tool
```

Set up a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
django==4.2.16
requests==2.32.3
beautifulsoup4==4.12.3
```

Configure the database (optional, PostgreSQL example in `settings.py`):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scraper_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Run the server:

```bash
python manage.py runserver
```

---

## 📖 Description

The scraper loops over a predefined list of Flipkart keywords (e.g., `"Headphone"`, `"Powerbanks"`, `"Smart Watches"`).  

For each keyword, it:

1. Fetches the Flipkart search results page.  
2. Extracts product URLs containing `/p/`.  
3. Scrapes details for the **first product** (configurable in `views.py`).  
4. Stores the data in the `Product` model.  
5. Returns a structured JSON response.  

### Example API call

```bash
curl http://localhost:8000/scrape/
```

### Example JSON response

```json
[
  {
    "query": "Headphone",
    "count": 1,
    "products": [
      {
        "name": "Boat Rockerz 450",
        "price": "₹1,299",
        "mrp": "₹2,999",
        "offer": "57% off",
        "seller_info": {
          "seller_name": "RetailNet",
          "rating": "4.3",
          "support_items": []
        },
        "ratings_reviews": {
          "overall": {
            "rating": "4.2",
            "star_icon": null,
            "ratings_text": "12,345 Ratings",
            "reviews_text": "1,234 Reviews"
          },
          "distribution": {},
          "feature_ratings": [],
          "reviews": []
        },
        "specifications": {
          "General": {
            "Model Name": "Rockerz 450"
          }
        },
        "product_url": "https://www.flipkart.com/..."
      }
    ]
  }
]
```

---

## 🗄 Database (Product Model)

The scraped data is stored in the `Product` model:

- **Text fields** → `name`, `price`, `mrp`, `offer`, `extra_off`, `delivery_date`, `delivery_note`, `product_url`  
- **JSON fields** → `seller_info`, `ratings_reviews`, `coupons`, `bank_offers`, `purchase_options`, `color_options`, `storage_options`, `ram_options`, `product_description`, `specifications`, `question_answer`  
- **URL fields** → `image_url`  

---

## 🧩 Notes

- By default, only the **first product per keyword** is scraped:  

  ```python
  for url in product_urls[:1]:
  ```

  Change `[:1]` to scrape more products.  

- The `/scrape/` endpoint is **CSRF-exempt**. Add authentication for production use.  
- Flipkart frequently changes its frontend → update CSS selectors when needed.  
- Use request throttling (`time.sleep(1)`) to avoid IP bans.  
- Respect Flipkart’s **terms of service**.  

---

## 🤝 Contributing

Contributions are welcome!  

1. Fork the repository.  
2. Create a new branch:  
   ```bash
   git checkout -b feature-branch
   ```
3. Commit changes:  
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to GitHub:  
   ```bash
   git push origin feature-branch
   ```
5. Create a Pull Request.  

✔️ Follow **PEP 8** style guidelines.  
✔️ Add tests where applicable.  

---

## 📜 License

This project is for **educational purposes only**.  
Check Flipkart’s policies before using scraped data for commercial purposes.  

---

## 👤 Author

**Piyush Kumar Saini**  
🔗 GitHub: [Piyushkumarsaini](https://github.com/Piyushkumarsaini)
