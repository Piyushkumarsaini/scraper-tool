from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup
from .models import *
import re
import traceback

# Utility to safely get text
def safe_get_text(tag, default="N/A"):
    return tag.get_text(strip=True) if tag else default

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36 Brave/1.82.166"
    )
}

def extract_product_urls(html_content, base_url="https://www.flipkart.com"):
    soup = BeautifulSoup(html_content, "html.parser")
    urls = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/p/" in href:
            full_url = base_url + href if href.startswith("/") else href
            urls.add(full_url)
    return list(urls)

@csrf_exempt
def scrape_flipkart_json(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed."}, status=405)

    query = request.GET.get("q")
    if not query:
        return JsonResponse({"error": "Missing product query (?q=...)"}, status=400)

    search_url = f"https://www.flipkart.com/search?q={query}"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch search page", "details": str(e)}, status=500)

    product_urls = extract_product_urls(response.text)
    if not product_urls:
        return JsonResponse({"message": "No products found."})

    # Scrape only the first product for demo
    results = []
    for url in product_urls[:1]:
        try:
            product_data = scrape_product_details(url)
            results.append(product_data)
        except Exception as e:
            results.append({
                "error": f"Failed to scrape product: {url}",
                "details": str(e),
                "trace": traceback.format_exc()
            })

    return JsonResponse({"query": query, "count": len(results), "products": results}, safe=False)


def scrape_product_details(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Failed to load product page: {e}")

    soup = BeautifulSoup(response.content, "html.parser")
    
    coupons = [safe_get_text(li) for li in soup.select("div.I+EQVr")]
    # Bank offers
    bank_offers = [safe_get_text(li) for li in soup.select("div.NYb6Oz li.kF1Ml8.col")]

    # Payment offers
    payments = [safe_get_text(li) for li in soup.select("div.HQijVm li.g11wDd")]

    # Delivery info
    delivery_div = soup.select_one("div.nRBH83")
    delivery_date = safe_get_text(delivery_div.select_one("span.Y8v7Fl")) if delivery_div else None
    delivery_note = safe_get_text(delivery_div.select_one("div.m-cM89")) if delivery_div else None
    
    # Build seller info dictionary
    seller = {
        "seller_name": safe_get_text(soup.select_one('#sellerName span span')),
        "rating": safe_get_text(soup.select_one('.XQDdHH')),
        "support_items": [
            safe_get_text(item) for item in soup.select('.fke1mx li .YhUgfO')
        ]
    }
    
    protect_info = {
    "protect_promise_fee": safe_get_text(soup.select_one('.QLGtsq span')),
    "delivery_text": safe_get_text(soup.select_one('.yiggsN'))
    }
# ------------------------------------------------------------- Ram ----------------------------------------------------------------------
    # RAM options for phone
    phone_ram_options = []
    for li in soup.select("li.aJWdJI[id$='-ram']"):
        a_tag = li.select_one("a")
        phone_ram_options.append({
            "ram_text": safe_get_text(li.select_one("div.V3Zflw")),
            "link": "https://www.flipkart.com" + a_tag["href"] if a_tag and a_tag.has_attr("href") else None
        })

    # RAM options for laptop
    laptop_ram_options = []
    for li in soup.select("li.aJWdJI[id*='system_memory']"):
        a_tag = li.select_one("a")
        laptop_ram_options.append({
            "ram_text": safe_get_text(li.select_one("div.V3Zflw")),
            "link": "https://www.flipkart.com" + a_tag["href"] if a_tag and a_tag.has_attr("href") else None
        })

    # Prefer phone RAM, fallback to laptop RAM
    ram_options = phone_ram_options if phone_ram_options else laptop_ram_options

        
    
    # Color options
    colors = []
    for li in soup.select("li.aJWdJI[id$='-color']"):
        color = {
            "name": safe_get_text(li.select_one("div.V3Zflw")),
            "image": li.select_one("img")["src"] if li.select_one("img") else None,
            "link": "https://www.flipkart.com" + li.select_one("a")["href"] if li.select_one("a") else None
        }
        colors.append(color)
        
    # Extract storage options
    storages = []
    for li in soup.select("li.aJWdJI[id$='-storage']"):
        storage = {
            "storage": safe_get_text(li.select_one("div.V3Zflw")),
            "link": "https://www.flipkart.com" + li.select_one("a")["href"] if li.select_one("a") else None
        }
        storages.append(storage)
        
# ----------------------------------------------------------------- purchase options -------------------------------------------------------
    # Purchase options
    purchase_options = []
    purchase_div = soup.find("div", class_="BRgXml")
    if purchase_div:
        for item in purchase_div.find_all("div", class_="-B1t91"):
            text = safe_get_text(item)
            if "₹" in text:
                option_type, option_value = text.split("₹", 1)
                purchase_options.append({
                    "type": option_type.strip(),
                    "value": "₹" + option_value.strip()
                })
                
    
    #----------------------------------------------- Specifications -----------------------------------------------------------------
    specifications = {}
    for section in soup.find_all("div", class_="GNDEQ-"):
        section_title = safe_get_text(section.find("div", class_="_4BJ2V+"))
        specs = {}
        table = section.find("table", class_="_0ZhAN9")
        if table:
            for row in table.find_all("tr", class_="WJdYP6"):
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = safe_get_text(cols[0])
                    value = " ".join([safe_get_text(li) for li in cols[1].find_all("li")]) or safe_get_text(cols[1])
                    specs[key] = value
        if specs:
            specifications[section_title] = specs


    #----------------------------------------------- Product Description -----------------------------------------------------------------
    
    product_description = []
    for description in soup.find_all("div", class_="pqHCzB"):
        # title = safe_get_text(description.find("div", class_="_9GQWrZ"))
        # descri = safe_get_text(description.find("div", class_="AoD2-N"))
        img_tag = description.find("div", class_="_0B07y7")
        # img_url = img_tag.find("img")["src"] if img_tag and img_tag.find("img") else None
        
        product_description.append({
            "title": safe_get_text(description.find("div", class_="_9GQWrZ")),
            "description": safe_get_text(description.find("div", class_="AoD2-N")),
            "description_image_url": img_tag.find("img")["src"] if img_tag and img_tag.find("img") else None 
        })
    
# -------------------- RATING & REVIEW BLOCK --------------------

    # -------------------- Overall Rating Block --------------------
    rating_block = soup.select_one('div.col-4-12')
    overall_rating = safe_get_text(rating_block.select_one('div.ipqd2A'))
    star_icon = safe_get_text(rating_block.select_one('div.u12NqW'))
    ratings_count = rating_block.select('div.row.j-aW8Z span')
    ratings_text = safe_get_text(ratings_count[0]) if len(ratings_count) > 0 else None
    reviews_text = safe_get_text(ratings_count[1]) if len(ratings_count) > 1 else None

    rating_data = {
        "rating": overall_rating,
        "star_icon": star_icon,
        "ratings_text": ratings_text,
        "reviews_text": reviews_text
    }

    # -------------------- Rating Distribution (5★ to 1★) --------------------
    stars = [safe_get_text(tag) for tag in soup.select('ul.lpANVI span.Fig8YH')]
    bars = soup.select('ul.GwkPFK span.DoUsN7')
    percentages = []
    for bar in bars:
        style = bar.get("style", "")
        match = re.search(r'width:(\d+(\.\d+)?)%', style)
        percentages.append(float(match.group(1)) if match else 0.0)

    counts = [safe_get_text(tag) for tag in soup.select('ul[class~="+psZUR"] div.BArk-j')]

    rating_distribution = {}
    for star, percent, count in zip(stars, percentages, counts):
        rating_distribution[star] = {
            "percentage": round(percent, 2),
            "count": count
        }

    # -------------------- Feature-wise Ratings --------------------
    feature_blocks = soup.select('a.col-3-12.zbCsdp.zsSYMX')
    feature_ratings = []
    for block in feature_blocks:
        feature_ratings.append({
            "rating": safe_get_text(block.select_one('text._2DdnFS')),
            "label": safe_get_text(block.select_one('div.NTiEl0'))
        })

    # -------------------- Reviews --------------------
    review_blocks = soup.find_all('div', class_='col EPCmJX')
    all_reviews = []

    for i, review in enumerate(review_blocks, 1):
        try:
            rating = safe_get_text(review.find('div', class_='XQDdHH Ga3i8K'))
            title = safe_get_text(review.find('p', class_='z9E0IG'))
            review_text = safe_get_text(review.select_one('div.ZmyHeo div > div'))
            reviewer_name = safe_get_text(review.find('p', class_='_2NsDsF AwS1CA'))
            location = safe_get_text(review.find('p', class_='MztJPv'))
            time_ago = safe_get_text(review.select_one('p._2NsDsF:not(.AwS1CA)'))

            image_urls = []
            image_divs = review.select('div.Be4x5X.d517go')
            for div in image_divs:
                style = div.get('style', '')
                match = re.search(r'url\((https://[^,]+)', style)
                if match:
                    image_urls.append(match.group(1))

            votes = review.select('span.tl9VpF')
            upvotes = votes[0].text.strip() if len(votes) > 0 else '0'
            downvotes = votes[1].text.strip() if len(votes) > 1 else '0'

            review_dict = {
                'Rating': rating,
                'Title': title,
                'Review': review_text,
                'Reviewer': reviewer_name,
                'Location': location,
                'Time Ago': time_ago,
                'Images': image_urls,
                'Upvotes': upvotes,
                'Downvotes': downvotes
            }

            all_reviews.append(review_dict)

        except Exception as e:
            print(f"Error in review #{i}: {e}")

    # -------------------- Final Dictionary --------------------
    final_data = {
        'overall_rating': rating_data,
        'rating_distribution': rating_distribution,
        'feature_ratings': feature_ratings,
        'reviews': all_reviews
    }

    # Image
    img_tags = soup.find_all("img", class_="_0DkuPH")
    image_url = [img["src"] for img in img_tags if img.get("src")]

    #---------------------------------------- question answer ------------------------------------------------------
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
    
 # -------------------- PRODUCT DATA --------------------
    product_data = {
        "name": safe_get_text(soup.select_one("h1._6EBuvT span.VU-ZEz")),
        "extra_off": safe_get_text(soup.select_one("div._2lX4N0")),
        "price": safe_get_text(soup.select_one("div.Nx9bqj.CxhGGd")),
        "mrp": safe_get_text(soup.select_one("div.hl05eU div.yRaY8j A6+E6v")),
        "offer": safe_get_text(soup.select_one("div.UkUFwK.WW8yVX")),
        "protect_info": protect_info,
        "ratings_reviews": final_data,
        "coupons": coupons,
        "bank_offers": bank_offers,
        "purchase_options": purchase_options,
        "color_options": colors,
        "storag_options": storages,
        "delivery_date": delivery_date,
        "delivery_note": delivery_note,
        "payment_offers": payments,
        "ram_options": ram_options,
        "highlight_items": [safe_get_text(li) for li in soup.select('.U\\+9u4y ._7eSDEz')],
        "seller_info": seller,
        "description": safe_get_text(soup.select_one('div._4gvKMe')),
        "product_description": product_description,
        "specifications": specifications,
        "question_answer": qa_list,
        "image_url": image_url,
        "product_url": url
    }
    
    a = soup.find_all('div', class_= 'WGBwfw')
    # print(a)
    # Product.objects.create(**product_data)
    return product_data