#!/usr/bin/env python
import requests
import json

class ChangelogScraper:
    def __init__(self):
        self.headers = {
            'accept': '/',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-nextjs-data': '1'
        }
        self.url = 'https://deepgram.com/_next/data/3Ocw7quqOZgC2tHlYRACS/changelog.json?slug=changelog'
        self.params = {'slug': 'changelog'}
        self.all_extracted_articles = []

    def fetch_data(self):
        response = requests.get(
            self.url,
            params=self.params,
            headers=self.headers,
            cookies={},
            allow_redirects=True
        )
        return response.json()

    def extract_info(self, article):
        title = article['title']
        paragraphs = []
        body_children = article['body']['value']['document']['children']

        for child in body_children:
            if child['type'] == 'paragraph':
                for span in child.get('children', []):
                    if span['type'] == 'span':
                        text = span.get('value', '')
                        if text:
                            paragraphs.append(text)

            elif child['type'] == 'list':
                for item in child.get('children', []):
                    if 'children' in item:
                        for sub_item in item['children']:
                            if sub_item['type'] == 'paragraph':
                                for span in sub_item.get('children', []):
                                    if span['type'] == 'span':
                                        text = span.get('value', '')
                                        if text:
                                            paragraphs.append(text)

        return {
            'title': title,
            'description': ' '.join(paragraphs),
        }

    def process_articles(self):
        data = self.fetch_data()
        for article in data['pageProps']['changelogs']['allTemplateChangelogs']:
            flat_article = self.extract_info(article)
            self.all_extracted_articles.append(flat_article)

    def save_articles(self, filename="all_articles.json"):
        with open(filename, "w") as f:
            f.write(json.dumps(self.all_extracted_articles))

def main():
    scraper = ChangelogScraper()
    scraper.process_articles()
    scraper.save_articles()

    # Save the first article to pretty_article.json
    with open("pretty_article.json", "w") as f:
        # json.dump(scraper.all_extracted_articles[0], indent=2, fp=f) for a single one
        json.dump(scraper.all_extracted_articles, indent=2, fp=f)

if __name__ == "__main__":
    main()


# to use it
scraper = ChangelogScraper()
scraper.process_articles()
scraper.save_articles("test_work.json")

# Print and save the first article with nice formatting
# print(json.dumps(scraper.all_extracted_articles[0], indent=2))
with open("pretty_article.json", "w") as f:
    json.dump(scraper.all_extracted_articles, indent=2, fp=f)