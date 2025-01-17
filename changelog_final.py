#!/usr/bin/env python
import requests
import json


# taken from website -- google chrome developer mode

# copy as fetch in vs code to see what it looks then refactor for python manipulation


#changelog.json --> important

headers = {
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
    'x-nextjs-data': '1'  # This is important for Next.js data fetching
}

# Build URL with proper parameters

# session embedded in URL
url = 'https://deepgram.com/_next/data/3pZMHpHpgb2-MN1JiWJIw/changelog.json'
params = {'slug': 'changelog'}

response = requests.get(
    url,
    params=params,
    headers=headers,
    cookies={},  # Add any required cookies here if needed
    allow_redirects=True
)

data = response.json()

def extract_info(article):
    # Extract title
    title = article['title']

    # Extract paragraphs
    paragraphs = []
    paragraphs_string = ""
    body_children = article['body']['value']['document']['children']

    for child in body_children:
        # If it's a paragraph type
        if child['type'] == 'paragraph':
            # Extract text from span
            for span in child.get('children', []):
                if span['type'] == 'span':
                    text = span.get('value', '')
                    if text:  # Only add non-empty strings
                        paragraphs.append(text)

        # If it's a list, process its items
        elif child['type'] == 'list':
            for item in child.get('children', []):
                if 'children' in item:
                    for sub_item in item['children']:
                        if sub_item['type'] == 'paragraph':
                            for span in sub_item.get('children', []):
                                if span['type'] == 'span':
                                    text = span.get('value', '')
                                    if text:  # Only add non-empty strings
                                        paragraphs.append(text)

    return {
        'title': title,
        'description': ' '.join(paragraphs),  # Join all paragraphs with space
    }

all_extracted_articles = []

# we are getting title and description
for article in data['pageProps']['changelogs']['allTemplateChangelogs']:
    # Using the data from your document
    # data = {'__typename': 'TemplateChangelogRecord', 'title': 'Deepgram Self-Hosted December 2024 Release (241226)', ...}  # Your full dictionary here
    flat_article = extract_info(article) # to get flatten article, the structure that is required:
    all_extracted_articles.append(flat_article) # apprend each extracted dictionary to all_extracted article to list
    # print("Title:", flat_article['title'])
    # print("\nContent:", flat_article['paragraphs'])

# saved in all_articles
with open("all_articles.json", "w") as f:
    f.write(json.dumps(all_extracted_articles))


# task2: adjust extract info to get id


# task3: Demonstrate how the scraped data can be migrated to Cycle’s own changelog feature.

# transform the json extracted to json format that is fitted to Cycle App so it can be fetch to Cycle App database


# TODO so : create a class and for the task 3 need to create a method in the class to transform the json that is being get from the method extract_info
#  to a suitable Json for the Cycle App json database structure