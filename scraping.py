import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import csv


class GitHubChangelogScraper:
    def __init__(self, output_dir="/Users/markojovanovic/PycharmProjects/scraper"):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.output_dir = output_dir

    def scrape_github_releases(self, repo_path: str):
        """
        Scrape GitHub releases page with corrected selectors for Vue.js
        """
        url = f'https://github.com/{repo_path}/releases'
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            releases = []

            # Find all release divs - using Vue.js specific structure
            release_divs = soup.find_all('div', {'class': ['release', 'label-group']})

            print(f"Found {len(release_divs)} releases")

            for release_div in release_divs:
                try:
                    # Get version title
                    title_elem = release_div.find('a', {'class': 'Link--primary'})
                    title = title_elem.text.strip() if title_elem else None

                    # Get date
                    date_elem = release_div.find('relative-time')
                    date = date_elem['datetime'] if date_elem else None

                    # Get description
                    desc_elem = release_div.find('div', {'class': 'markdown-body'})
                    description = desc_elem.get_text(strip=True) if desc_elem else None

                    # Get tags/labels
                    tag_elems = release_div.find_all('span', {'class': 'Label'})
                    tags = [tag.text.strip() for tag in tag_elems if tag]

                    # Create release data structure
                    release_data = {
                        'version': title,
                        'date': date,
                        'description': description,
                        'tags': tags,
                        'url': f"https://github.com/{repo_path}/releases/tag/{title}" if title else None
                    }

                    releases.append(release_data)
                    print(f"Processed release: {title}")

                except Exception as e:
                    print(f"Error processing release: {str(e)}")
                    continue

            # Save as JSON
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_file = os.path.join(self.output_dir, f'github_releases_{timestamp}.json')

            result = {
                'repository': repo_path,
                'scrape_date': datetime.now().isoformat(),
                'total_releases': len(releases),
                'releases': releases
            }

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            # Save as CSV
            csv_file = os.path.join(self.output_dir, f'github_releases_{timestamp}.csv')
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['version', 'date', 'description', 'tags', 'url'])
                writer.writeheader()
                for release in releases:
                    # Convert tags list to string for CSV
                    release_copy = release.copy()
                    release_copy['tags'] = ', '.join(release_copy['tags'])
                    writer.writerow(release_copy)

            print(f"\nScraped {len(releases)} releases from {repo_path}")
            print(f"Data saved to:")
            print(f"JSON: {json_file}")
            print(f"CSV: {csv_file}")

            # Print first release as sample
            if releases:
                print("\nSample of first release:")
                print(json.dumps(releases[0], indent=2))

            return releases

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return []


# Example usage
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = "/Users/markojovanovic/PycharmProjects/scraper"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize scraper
    scraper = GitHubChangelogScraper(output_dir=output_dir)

    # Try Vue.js repository
    scraper.scrape_github_releases('vuejs/vue')