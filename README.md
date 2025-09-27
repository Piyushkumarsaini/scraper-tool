🛒 Flipkart Scraper Tool (Django)
A Django-based backend project for scraping product data from Flipkart.It fetches product details such as name, price, offers, ratings, reviews, seller info, specifications, images, Q&A, and more.The data is stored in the database using Django models and can also be returned as JSON via an API endpoint.

🚀 Features

Scrapes detailed product information:
Name, Price, MRP, Offers
Coupons & Bank Offers
Delivery details
Seller info
RAM, Color, Storage, Purchase options
Ratings & Review blocks (with distribution + feature-wise ratings)
Product specifications
Product description (with images)
Q&A section
Product images


Saves scraped data into the database (Product model).
Provides JSON API endpoint for scraping.


📂 Project Structure
scraper-tool/
├── manage.py
├── requirements.txt
├── scraper_tool/        # Main Django app folder
│   ├── models.py        # Product model
│   ├── views.py         # Scraping + API logic
│   ├── urls.py          # API routes
│   └── ...
└── README.md


🛠 Requirements

Python 3.9+
Django 4.x+
Libraries:
requests
beautifulsoup4




⚙️ Setup

Clone the repository:
git clone https://github.com/Piyushkumarsaini/scraper-tool.git
cd scraper-tool


Install dependencies:
pip install -r requirements.txt


Apply migrations:
python manage.py makemigrations
python manage.py migrate


Run the server:
python manage.py runserver




📊 How It Works
The scraper loops over a predefined list of Flipkart keywords (e.g., Headphones, Powerbanks, Smart Watches).
For each keyword:

Fetches Flipkart search results.
Extracts the first product link.
Scrapes product details.
Saves product data in the database.
Returns structured JSON.


📦 Example API Response
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
          "rating": "4.3"
        },
        "ratings_reviews": {
          "overall": {
            "rating": "4.2",
            "reviews_text": "12,345 Reviews"
          }
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


🗄 Database (Product Model)
The scraped product is saved in the Product model with fields such as:

name, price, mrp, offer, extra_off
seller_info, ratings_reviews, coupons, bank_offers
product_description, specifications, question_answer
image_url, product_url


🧩 Notes

Currently scrapes only the first product per keyword (demo mode).You can change this in views.py:
for url in product_urls[:1]:

Increase the range to scrape more products.

Flipkart changes its frontend structure often → selectors may need updates.

Add request throttling (time.sleep) if you plan large-scale scraping.

Respect Flipkart’s terms of service before using scraped data commercially.



🤝 Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes and commit (git commit -m 'Add new feature').
Push to the branch (git push origin feature-branch).
Create a Pull Request.

Please follow PEP 8 style guidelines and include tests where applicable.

📜 License
This project is for educational purposes only.Check Flipkart’s policies before using scraped data for commercial purposes.

👤 Author
Piyush Kumar Saini🔗 GitHub: Piyushkumarsaini