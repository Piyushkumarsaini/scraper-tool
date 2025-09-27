from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup
from .models import *
import re
import traceback
from urllib.parse import urljoin, quote_plus

# Utility to safely get text
def safe_get_text(tag, default=None):
    if tag is None:
        return default
    text = tag.get_text(separator=' ', strip=True)
    return text if text not in ("", "N/A") else default

def dict_remove_empty(dic):
    return {
        k: v for k, v in dic.items()
        if v not in (None, "", [], {}, "N/A")
    }
    
def safe_attr(tag, attr, default=None):
    if tag and tag.has_attr(attr):
        return tag.get(attr)
    return default

def _extract_style_url(style_text):
    if not style_text:
        return None
    m = re.search(r'url\((?:["\']?)(https?://[^)"\']+)(?:["\']?)\)', style_text)
    return m.group(1) if m else None

def extract_product_urls(html_content, base_url="https://www.flipkart.com"):
    soup = BeautifulSoup(html_content, "html.parser")
    urls = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        # Flipkart product detail pages often contain '/p/' in path
        if "/p/" in href:
            full_url = base_url + href if href.startswith("/") else href
            urls.add(full_url)
    return list(urls)
# ===================================================== HEADERS =========================================================================
HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36 Brave/1.82.166"
    )
}
# ====================================================================================================================================
@csrf_exempt
def scrape_flipkart_json(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed."}, status=405)

    # query = request.GET.get("q")
    # if not query:
    #     return JsonResponse({"error": "Missing product query (?q=...)"}, status=400)

    keywords = [
        "Headphone",
        "Headsets",
        "Powerbanks",
        "Mobile Cables",
        "Smart Watches",
        "Smart Bands",
        "Gaming Laptops",
        "Televisions",
        "Mobile Cases",
        "Smart Headphones",
        "Apple iPads",
        "Printers",
        "Mouse",
        "Mobile Holders",
        "Screen Guards",
        "Memory Cards",
        "Mobile Chargers",
        "Smart Glasses (VR)",
        "Weighing Scale",
        "Accessories",
        "External Hard Disks",
        "Pendrives",
        "Laptop Bags",
        "Laptop Skins & Decals",
        "Monitors",
        "Routers",
        "Desktop PCs",
        "Lens",
        "BP Monitors",
        "Tripods",
        "Google Nest"
        ]

    # for query in keywords:
    #     search_url = f"https://www.flipkart.com/search?q={query}"
    #     try:
    #         response = requests.get(search_url, headers=HEADERS, timeout=10)
    #         response.raise_for_status()
    #     except requests.RequestException as e:
    #         return JsonResponse({"error": "Failed to fetch search page", "details": str(e)}, status=500)
    final_results = []
    for query in keywords:
        search_url = f"https://www.flipkart.com/search?q={query}"
        try:
            response = requests.get(search_url, headers=HEADERS)
            response.raise_for_status()
        except requests.RequestException as e:
            final_results.append({
                "query": query,
                "error": "Failed to fetch search page",
                "details": str(e)
            })
            continue

        # product_urls = extract_product_urls(response.text)
        # if not product_urls:
        #     return JsonResponse({"message": "No products found."})
        product_urls = extract_product_urls(response.text)
        if not product_urls:
            final_results.append({
                "query": query,
                "message": "No products found."
            })
            continue
        
        # Scrape only the first product for demo
        # results = []
        # for url in product_urls[:1]:
        #     try:
        #         product_data = scrape_product_details(url)
        #         results.append(product_data)
        #     except Exception as e:
        #         results.append({
        #             "error": f"Failed to scrape product: {url}",
        #             "details": str(e),
        #             "trace": traceback.format_exc()
        #         })
        # return JsonResponse({"query": query, "count": len(results), "products": results}, safe=False)
        
        products = []
        for url in product_urls[:1]:
            try:
                product_data = scrape_product_details(url)
                products.append(product_data)
            except Exception as e:
                products.append({
                    "error": f"Failed to scrape product: {url}",
                    "details": str(e),
                    "trace": traceback.format_exc()
                })

        final_results.append({
            "query": query,
            "count": len(products),
            "products": products
        })

    return JsonResponse(final_results, safe=False)

def scrape_product_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Failed to load product page: {e}")

    soup = BeautifulSoup(response.content, "html.parser")
# =======================================================================================================================================    
    coupons = [safe_get_text(li) for li in soup.select("div.I+EQVr")]   
    # bank offers / payments — defensive
    bank_offers = [safe_get_text(li) for li in soup.select("div.NYb6Oz li.kF1Ml8.col")]
    payments = [safe_get_text(li) for li in soup.select("div.HQijVm li.g11wDd")]
    services = [safe_get_text(item) for item in soup.select('.C3EUFP li .YhUgfO')]
    payment_offers = payments or services
    
# =======================================================================================================================================    
    # Delivery info
    delivery_date = None
    delivery_note = None
    delivery_div = soup.select_one("div.nRBH83")
    if delivery_div:
        span = delivery_div.select_one("span.Y8v7Fl")
        delivery_date = safe_get_text(span)
        note_div = delivery_div.select_one("div.m-cM89")
        delivery_note = safe_get_text(note_div)
  
# =======================================================================================================================================    
    # Seller info (defensive)
    seller_name = None
    seller_name_tag = soup.select_one('#sellerName span span') or soup.select_one('#sellerName')
    if seller_name_tag:
        seller_name = safe_get_text(seller_name_tag)
    seller_rating = safe_get_text(soup.select_one('.XQDdHH'))
    seller_support_items = [safe_get_text(li) for li in soup.select('.fke1mx li')]
    
    seller = {
        "seller_name": seller_name,
        "rating": seller_rating,
        "support_items": [s for s in seller_support_items if s]
    }
# =======================================================================================================================================
# ------------------------------------------------------------- Ram ----------------------------------------------------------------------
    # RAM options example (phone or laptop)
    ram_options = []
    for li in soup.select("li[id$='-ram'], li[id*='system_memory']"):
        text = safe_get_text(li.select_one("div.V3Zflw")) or safe_get_text(li)
        link = None
        a_tag = li.find("a")
        if a_tag and a_tag.has_attr("href"):
            link = urljoin("https://www.flipkart.com", a_tag["href"])
        ram_options.append({"ram_text": text, "link": link})


#  ======================================================================================================================       
    # Colors (defensive)
    colors = []
    for li in soup.select("li[id$='-color']"):
        name = safe_get_text(li.select_one("div.V3Zflw"))
        img = safe_attr(li.select_one("img"), "src")
        a = li.select_one("a")
        link = urljoin("https://www.flipkart.com", a["href"]) if a and a.has_attr("href") else None
        colors.append({"name": name, "image": img, "link": link})
# =======================================================================================================================================        
    # Storage options
    storages = []
    for li in soup.select("li[id$='-storage']"):
        stor = safe_get_text(li.select_one("div.V3Zflw"))
        a = li.select_one("a")
        link = urljoin("https://www.flipkart.com", a["href"]) if a and a.has_attr("href") else None
        storages.append({"storage": stor, "link": link})
  
# =======================================================================================================================================      
# ----------------------------------------------------------------- purchase options -------------------------------------------------------
    # Purchase options example (defensive)
    purchase_options = []
    purchase_div = soup.find("div", class_="BRgXml")
    if purchase_div:
        for item in purchase_div.find_all("div", class_="-B1t91"):
            text = safe_get_text(item) or ""
            if "₹" in text:
                parts = text.split("₹", 1)
                option_type = parts[0].strip()
                option_value = "₹" + parts[1].strip() if len(parts) > 1 else None
                purchase_options.append({"type": option_type, "value": option_value})
            else:
                if text:
                    purchase_options.append({"type": text, "value": None})
# =======================================================================================================================================
    #----------------------------------------------- Specifications -----------------------------------------------------------------
    # Specifications (robust)
    specifications = {}
    for section in soup.select("div.GNDEQ-, div.someOtherSpecClass"):
        title_tag = section.find('div', class_='_4BJ2V') or section.find('div')
        section_title = safe_get_text(title_tag) or "Specifications"
        specs = {}
        table = section.find("table")
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all(["td","th"])
                if len(cols) >= 2:
                    key = safe_get_text(cols[0])
                    # value may be list items or text
                    value_items = [safe_get_text(li) for li in cols[1].find_all("li")] if cols[1].find_all("li") else []
                    value = " ".join([v for v in value_items if v]) or safe_get_text(cols[1])
                    if key:
                        specs[key] = value
        if specs:
            specifications[section_title] = specs

# =======================================================================================================================================
    #----------------------------------------------- Product Description -----------------------------------------------------------------
    
    product_description = []
    for description in soup.find_all("div", class_="pqHCzB"):
        img_tag = description.find("div", class_="_0B07y7")
        product_description.append({
            "title": safe_get_text(description.find("div", class_="_9GQWrZ")),
            "description": safe_get_text(description.find("div", class_="AoD2-N")),
            "description_image_url": img_tag.find("img")["src"] if img_tag and img_tag.find("img") else None 
        })
        
# =======================================================================================================================================      
# -------------------- RATING & REVIEW BLOCK --------------------
    # Ratings & reviews — DO NOT return early if missing
    rating_block = soup.select_one('div.col-4-12')
    overall_rating = safe_get_text(rating_block.select_one('div.ipqd2A')) if rating_block else None
    star_icon = safe_get_text(rating_block.select_one('div.u12NqW')) if rating_block else None
    ratings_text, reviews_text = None, None
    if rating_block:
        ratings_count = rating_block.select('div.row.j-aW8Z span')
        if ratings_count:
            ratings_text = safe_get_text(ratings_count[0]) if len(ratings_count) > 0 else None
            reviews_text = safe_get_text(ratings_count[1]) if len(ratings_count) > 1 else None
# =======================================================================================================================================
    # Rating distribution (attempt)
    rating_distribution = {}
    stars = [safe_get_text(tag) for tag in soup.select('ul.lpANVI span.Fig8YH')]
    bars = soup.select('ul.GwkPFK span.DoUsN7')
    percentages = []
    for bar in bars:
        style = bar.get("style", "") or ""
        m = re.search(r'width\s*:\s*(\d+(\.\d+)?)%', style)
        percentages.append(float(m.group(1)) if m else 0.0)
    counts = [safe_get_text(tag) for tag in soup.select('div.BArk-j, div.someCountClass')]
    for star, percent, count in zip(stars, percentages, counts):
        rating_distribution[star] = {"percentage": round(percent,2), "count": count}

# =======================================================================================================================================
    # -------------------- Feature-wise Ratings --------------------
    feature_blocks = soup.select('a.col-3-12.zbCsdp.zsSYMX')
    feature_ratings = []
    for block in feature_blocks:
        feature_ratings.append({
            "rating": safe_get_text(block.select_one('text._2DdnFS')),
            "label": safe_get_text(block.select_one('div.NTiEl0'))
        })

# =======================================================================================================================================

    # Reviews (best-effort)
    all_reviews = []
    review_blocks = soup.select('div.col.EPCmJX') or soup.select('div.someReviewClass')
    for review in review_blocks:
        try:
            rating = safe_get_text(review.select_one('div.XQDdHH'))
            title = safe_get_text(review.select_one('p.z9E0IG'))
            review_text = safe_get_text(review.select_one('div.ZmyHeo'))
            reviewer_name = safe_get_text(review.select_one('p._2NsDsF.AwS1CA')) or safe_get_text(review.select_one('p._2NsDsF'))
            location = safe_get_text(review.select_one('p.MztJPv'))
            time_ago = safe_get_text(review.select_one('p._2NsDsF:not(.AwS1CA)')) or None

            # images from style attr
            image_urls = []
            for div in review.select('div.Be4x5X.d517go'):
                url_in_style = _extract_style_url(div.get('style',''))
                if url_in_style:
                    image_urls.append(url_in_style)

            votes = [v.get_text(strip=True) for v in review.select('span.tl9VpF')]
            upvotes = votes[0] if len(votes)>0 else '0'
            downvotes = votes[1] if len(votes)>1 else '0'

            all_reviews.append({
                'rating': rating,
                'title': title,
                'review': review_text,
                'reviewer': reviewer_name,
                'location': location,
                'time_ago': time_ago,
                'images': image_urls,
                'upvotes': upvotes,
                'downvotes': downvotes
            })
        except Exception as e:
            # don't stop on a single broken review
            print("Error parsing a review:", e)

# =======================================================================================================================================
    # Images (product)
    image_url = []
    for img in soup.find_all("img", class_="_0DkuPH"):
        src = safe_attr(img, "src")
        if src and ('/images' in src or 'flipkart' in src or src.startswith('http')):
            image_url.append(src)

# =======================================================================================================================================
    qa_blocks = soup.find_all('div', class_='BZMA+t')
    qa_list = []  # To store all Q&A pairs
    for block in qa_blocks:
        question_tag = block.find('div', class_='wys2hv _43gOsC')
        if question_tag:
            question = question_tag.get_text(separator=' ', strip=True).replace('Q:', '').strip()
        else:
            question = "No question found"
        answer_tag = block.find('div', class_='JxAXcP')
        if answer_tag:
            answer = answer_tag.get_text(separator=' ', strip=True).replace('A:', '').strip()
        else:
            answer = "No answer found"
        question_answer = {
            "question": question,
            "answer": answer
        }
        qa_list.append(question_answer)
    
# =======================================================================================================================================
    product_datas = {
        "name": safe_get_text(soup.select_one("h1._6EBuvT span.VU-ZEz")) or safe_get_text(soup.select_one("h1")),
        "extra_off": safe_get_text(soup.select_one("div._2lX4N0")),
        "price": safe_get_text(soup.select_one("div.Nx9bqj.CxhGGd")),
        "mrp": safe_get_text(soup.select_one("div.hl05eU div.yRaY8j A6+E6v")),
        "offer": safe_get_text(soup.select_one("div.UkUFwK.WW8yVX")),
        "protect_info": {
            "protect_promise_fee": safe_get_text(soup.select_one('.QLGtsq span')),
            "delivery_text": safe_get_text(soup.select_one('.yiggsN'))
        },
        "ratings_reviews": {
            "overall": {"rating": overall_rating, "star_icon": star_icon, "ratings_text": ratings_text, "reviews_text": reviews_text},
            "distribution": rating_distribution,
            "feature_ratings": feature_ratings,
            "reviews": all_reviews
        },
        "coupons": [c for c in coupons if c],
        "bank_offers": [b for b in bank_offers if b],
        "purchase_options": purchase_options,
        "color_options": colors,
        "storage_options": storages,
        "delivery_date": delivery_date,
        "delivery_note": delivery_note,
        "payment_offers": payment_offers,
        "ram_options": ram_options,
        "seller_info": seller,
        "product_description": product_description,
        "specifications": specifications,
        "question_answer": qa_list,
        "image_url": image_url,
        "product_url": url
    }
    product_data = dict_remove_empty(product_datas)
    # Product.objects.update_or_create(**product_datas)

    # This will update if product_url exists, otherwise create a new one
    Product.objects.update_or_create(
        product_url=product_data.get("product_url"),
        defaults=product_data
    )

    return product_data
