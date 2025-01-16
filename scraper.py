import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_deepgram_changelog():
    url = "https://deepgram.com/changelog"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        # Fetch the page
        logger.info(f"Fetching {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Log response status and content length
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Content length: {len(response.text)} bytes")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Debug: Print the first bit of HTML
        logger.debug("First 500 characters of HTML:")
        logger.debug(response.text[:500])

        # Find all changelog entries using multiple possible selectors
        entries = []
        # Try different possible container selectors
        containers = (
                soup.find('main') or
                soup.find('div', {'role': 'main'}) or
                soup.find('div', class_='container') or
                soup
        )

        if containers:
            # Look for changelog items with multiple possible class patterns
            changelog_items = containers.find_all(['div', 'article'], class_=lambda x: x and any(
                pattern in str(x).lower()
                for pattern in ['changelog', 'update', 'release', 'entry', 'post']
            ))

            # If still no items found, try broader search
            if not changelog_items:
                changelog_items = containers.find_all(['div', 'article'])

            logger.info(f"Found {len(changelog_items)} potential changelog items")

            for item in changelog_items:
                try:
                    # Extract date - try multiple patterns
                    date = None
                    date_element = (
                            item.find('time') or
                            item.find(['p', 'span', 'div'], class_=lambda x: x and any(
                                word in str(x).lower() for word in ['date', 'time', 'posted', 'published']
                            ))
                    )
                    if date_element:
                        date = date_element.get('datetime', '') or date_element.text.strip()

                    # Extract title
                    title_element = (
                            item.find(['h1', 'h2', 'h3']) or
                            item.find(class_=lambda x: x and 'title' in str(x).lower())
                    )
                    title = title_element.text.strip() if title_element else ''

                    # Skip if no title found
                    if not title:
                        continue

                    # Extract description
                    desc_element = (
                            item.find(class_=lambda x: x and any(
                                word in str(x).lower()
                                for word in ['content', 'description', 'text', 'body']
                            )) or
                            item.find(['p', 'div'], class_=lambda x: x and 'mt-' in str(x))
                    )
                    description = desc_element.text.strip() if desc_element else ''

                    # Extract tags
                    tags = []
                    tag_elements = item.find_all(['span', 'div'], class_=lambda x: x and any(
                        word in str(x).lower() for word in ['tag', 'label', 'category', 'badge']
                    ))
                    for tag in tag_elements:
                        tag_text = tag.text.strip()
                        if tag_text and len(tag_text) < 30:  # Skip if too long (likely not a tag)
                            tags.append(tag_text)

                    entry = {
                        'date': date,
                        'title': title,
                        'description': description,
                        'tags': tags,
                        'url': url  # Include source URL
                    }

                    entries.append(entry)
                    logger.debug(f"Processed entry: {title}")

                except Exception as e:
                    logger.error(f"Error parsing entry: {str(e)}")
                    continue

        # Sort entries by date if possible
        try:
            entries.sort(key=lambda x: datetime.strptime(x['date'], '%B %d, %Y') if x['date'] else datetime.max,
                         reverse=True)
        except:
            logger.warning("Could not sort entries by date")

        # Export to JSON
        output_file = "deepgram_changelog.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'total_entries': len(entries)
                },
                'entries': entries
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully scraped {len(entries)} entries")
        logger.info(f"Data saved to {output_file}")

        # Print sample entries
        if entries:
            logger.info("\nFirst entry sample:")
            print(json.dumps(entries[0], indent=2))
        else:
            logger.warning("No entries were found!")
            # Debug: Print page title and some content
            page_title = soup.title.string if soup.title else "No title found"
            logger.debug(f"Page title: {page_title}")

    except requests.RequestException as e:
        logger.error(f"Error fetching the page: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    scrape_deepgram_changelog()