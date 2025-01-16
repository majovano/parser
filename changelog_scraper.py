import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import Dict, List, Optional


class ChangelogScraper:
    def __init__(self, url: str):
        self.url = url
        self.domain = self._extract_domain(url)

    def _extract_domain(self, url: str) -> str:
        """Extract the domain name from URL to identify the site."""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else ''

    def _fetch_page(self) -> Optional[str]:
        """Fetch the changelog page content."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def _parse_deepgram(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Deepgram's changelog format."""
        entries = []
        changelog_items = soup.find_all('div', class_='changelog-item')

        for item in changelog_items:
            # Extract date
            date_element = item.find('div', class_='changelog-date')
            date_str = date_element.text.strip() if date_element else ''

            # Extract title
            title_element = item.find('h3')
            title = title_element.text.strip() if title_element else ''

            # Extract description
            desc_element = item.find('div', class_='changelog-description')
            description = desc_element.text.strip() if desc_element else ''

            # Extract tags
            tags = []
            tag_elements = item.find_all('span', class_='changelog-tag')
            for tag in tag_elements:
                tags.append(tag.text.strip())

            entries.append({
                'date': date_str,
                'title': title,
                'description': description,
                'tags': tags
            })

        return entries

    def _parse_june(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse June.so's changelog format."""
        entries = []
        changelog_items = soup.find_all('article')

        for item in changelog_items:
            # Extract date
            date_element = item.find('time')
            date_str = date_element['datetime'] if date_element else ''

            # Extract title
            title_element = item.find('h2')
            title = title_element.text.strip() if title_element else ''

            # Extract description
            desc_element = item.find('div', class_='prose')
            description = desc_element.text.strip() if desc_element else ''

            entries.append({
                'date': date_str,
                'title': title,
                'description': description,
                'tags': []  # June.so doesn't seem to use tags in their changelog
            })

        return entries

    def _parse_clay(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Clay's changelog format."""
        entries = []
        changelog_items = soup.find_all('div', class_='changelog-entry')

        for item in changelog_items:
            # Extract date
            date_element = item.find('div', class_='date')
            date_str = date_element.text.strip() if date_element else ''

            # Extract title
            title_element = item.find('h3')
            title = title_element.text.strip() if title_element else ''

            # Extract description
            desc_element = item.find('div', class_='description')
            description = desc_element.text.strip() if desc_element else ''

            # Extract tags
            tags = []
            tag_elements = item.find_all('span', class_='tag')
            for tag in tag_elements:
                tags.append(tag.text.strip())

            entries.append({
                'date': date_str,
                'title': title,
                'description': description,
                'tags': tags
            })

        return entries

    def scrape(self) -> List[Dict]:
        """Main method to scrape changelog entries."""
        content = self._fetch_page()
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')

        # Select parser based on domain
        if 'deepgram.com' in self.domain:
            return self._parse_deepgram(soup)
        elif 'june.so' in self.domain:
            return self._parse_june(soup)
        elif 'clay.com' in self.domain:
            return self._parse_clay(soup)
        else:
            print(f"No parser implemented for domain: {self.domain}")
            return []

    def export_json(self, filename: str):
        """Export scraped changelog entries to JSON file."""
        entries = self.scrape()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)


def main():
    # Example usage
    urls = [
        'https://deepgram.com/changelog',
        'https://changelog.june.so',
        'https://www.clay.com/changelog'
    ]

    for url in urls:
        print(f"\nScraping {url}...")
        scraper = ChangelogScraper(url)
        entries = scraper.scrape()

        if entries:
            output_file = f"changelog_{scraper.domain.replace('.', '_')}.json"
            scraper.export_json(output_file)
            print(f"Exported {len(entries)} entries to {output_file}")
        else:
            print("No entries found or error occurred")


if __name__ == "__main__":
    main()