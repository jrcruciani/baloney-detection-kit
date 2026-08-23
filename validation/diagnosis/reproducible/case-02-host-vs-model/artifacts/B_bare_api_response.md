Here's a Python function that scrapes product pricing with proper headers, error handling, and respect for the target server:

```python
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin

def scrape_product_prices(
    base_url: str,
    product_selector: str,
    price_selector: str,
    name_selector: Optional[str] = None,
    delay: float = 1.0
) -> List[Dict[str, str]]:
    """
    Scrape product pricing from an e-commerce website.

    Args:
        base_url: The URL of the product listing page
        product_selector: CSS selector for individual product containers
        price_selector: CSS selector for price within each product
        name_selector: CSS selector for product name (optional)
        delay: Time to wait between requests in seconds

    Returns:
        List of dictionaries containing product name and price
    """

    # Reasonable User-Agent header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    products = []

    try:
        # Add delay to be respectful of the server
        time.sleep(delay)

        # Make the request
        response = requests.get(
            base_url,
            headers=headers,
            timeout=30  # 30 second timeout
        )

        # Check if request was successful
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product containers
        product_elements = soup.select(product_selector)

        if not product_elements:
            print(f"Warning: No products found with selector '{product_selector}'")
            return products

        for product in product_elements:
            try:
                # Extract price
                price_element = product.select_one(price_selector)
                if not price_element:
                    continue

                price_text = price_element.get_text(strip=True)

                # Extract name if selector provided
                product_name = "Unknown"
                if name_selector:
                    name_element = product.select_one(name_selector)
                    if name_element:
                        product_name = name_element.get_text(strip=True)

                products.append({
                    'name': product_name,
                    'price': price_text
                })

            except Exception as e:
                print(f"Error parsing product: {e}")
                continue

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out for {base_url}")
    except requests.exceptions.ConnectionError:
        print(f"Error: Connection failed for {base_url}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if response.status_code == 403:
            print("Access forbidden - may need to adjust headers")
        elif response.status_code == 429:
            print("Rate limited - increase delay between requests")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return products


def scrape_multiple_pages(
    base_url: str,
    product_selector: str,
    price_selector: str,
    name_selector: Optional[str] = None,
    num_pages: int = 1,
    page_param: str = "page",
    delay: float = 1.0
) -> List[Dict[str, str]]:
    """
    Scrape multiple pages of products.

    Args:
        base_url: Base URL for pagination
        product_selector: CSS selector for product containers
        price_selector: CSS selector for prices
        name_selector: CSS selector for product names
        num_pages: Number of pages to scrape
        page_param: URL parameter name for pagination
        delay: Delay between requests

    Returns:
        Combined list of products from all pages
    """
    all_products = []

    for page in range(1, num_pages + 1):
        page_url = f"{base_url}?{page_param}={page}" if page > 1 else base_url

        print(f"Scraping page {page}...")
        products = scrape_product_prices(
            base_url=page_url,
            product_selector=product_selector,
            price_selector=price_selector,
            name_selector=name_selector,
            delay=delay
        )

        if not products:
            print(f"No products found on page {page}, stopping pagination")
            break

        all_products.extend(products)

    return all_products


# Example usage:
if __name__ == "__main__":
    # Example for a hypothetical e-commerce site
    # Note: These selectors need to be adjusted for your target site

    base_url = "https://example.com/products"

    products = scrape_multiple_pages(
        base_url=base_url,
        product_selector=".product-card",      # Adjust based on target site
        price_selector=".product-price",       # Adjust based on target site
        name_selector=".product-title",        # Adjust based on target site
        num_pages=5,
        delay=1.5  # Be respectful with delays
    )

    # Print results
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name']}: {product['price']}")

    print(f"\nTotal products scraped: {len(products)}")
```

Key features of this implementation:

1. **Proper User-Agent**: Uses a modern browser User-Agent string that's reasonable for automated scraping
2. **Error Handling**: Catches various network issues (timeout, connection, HTTP, etc.)
3. **Rate Limiting**: Includes configurable delays between requests
4. **Flexibility**: Uses CSS selectors that can be adjusted for different sites
5. **Pagination Support**: Can handle multiple pages
6. **Type Hints**: Makes the code more maintainable
7. **Session Configuration**: Proper headers including Do Not Track and Accept headers

**Important usage notes:**

- Adjust the CSS selectors (`product_selector`, `price_selector`, `name_selector`) to match your target site's HTML structure
- Set appropriate delays (1-5 seconds) to avoid overwhelming the server
- Monitor the response status codes and adjust if you get 429 (Too Many Requests)
- Consider using sessions if you need to maintain cookies between requests
- Always check the site's `robots.txt` file even with permission
- Implement proper logging instead of print statements for production use