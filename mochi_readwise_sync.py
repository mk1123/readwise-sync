import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import json
import os
import logging

# Constants
READWISE_API_KEY = os.environ["READWISE_API_KEY"]
MOCHI_API_KEY = os.environ["MOCHI_API_KEY"]
MOCHI_DECK_ID = "Snf3dHYh" # Articles deck

READWISE_API_URL = "https://readwise.io/api/v3/list/"
MOCHI_API_URL = "https://app.mochi.cards/api/cards"

# After constants
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Helper function to format card content
def format_card_content(document):
    # Calculate reading time in minutes
    word_count = document.get('word_count') or 0
    reading_time = round(word_count / 300)
    reading_time = max(1, reading_time)  # Minimum 1 minute
    
    content = f"[{document['title']}]({document['url']})\n"
    content += f"Reading time: {reading_time} min\n"
    content += "Summary:\n```\n" + (document['summary'] or "No summary available") + "\n```\n"
    content += f"Reading progress: {document['reading_progress']*100:.1f}%\n"
    content += f"Notes: {document['notes']}"
    return content

# Helper function to create a Mochi card
def create_mochi_card(content):
    api_key = MOCHI_API_KEY + ":"
    auth = HTTPBasicAuth(api_key, "")
    data = {
        "content": content,
        "deck-id": MOCHI_DECK_ID
    }
    response = requests.post(MOCHI_API_URL, auth=auth, json=data)
    return response.json()

# Helper function to update a Mochi card
def update_mochi_card(card_id, content=None, archived=None):
    api_key = MOCHI_API_KEY + ":"
    auth = HTTPBasicAuth(api_key, "")
    data = {}
    if content is not None:
        data["content"] = content
    if archived is not None:
        data["archived?"] = archived
    
    response = requests.post(f"{MOCHI_API_URL}/{card_id}", auth=auth, json=data)
    return response.json()

# Helper function to get all Mochi cards in the deck
def get_mochi_cards():
    api_key = MOCHI_API_KEY + ":"
    auth = HTTPBasicAuth(api_key, "")
    all_cards = []
    bookmark = None

    while True:
        params = {"deck-id": MOCHI_DECK_ID}
        if bookmark:
            params["bookmark"] = bookmark

        response = requests.get(MOCHI_API_URL, auth=auth, params=params)
        data = response.json()

        if not data["docs"]:
            break
        
        all_cards.extend(data["docs"])
        
        # Check if there are more pages
        bookmark = data.get("bookmark")
            
    logging.debug(f"Retrieved {len(all_cards)} total cards across all pages")
    return all_cards

def get_readwise_documents(timestamp):
    headers = {
        "Authorization": f"Token {READWISE_API_KEY}"
    }
    params = {
        "updatedAfter": timestamp,
        "category": "article",
    }
    
    all_documents = []
    next_cursor = None
    
    while True:
        if next_cursor:
            params["pageCursor"] = next_cursor
            
        response = requests.get(READWISE_API_URL, headers=headers, params=params)
        data = response.json()
        
        documents = data["results"]
        if not documents:
            break
            
        all_documents.extend(documents)
        next_cursor = data.get("nextPageCursor")
        
        if not next_cursor:
            break
            
    logging.info(f"Found {len(all_documents)} updated documents in Readwise")
    return all_documents

def main():
    # get timestamp for one year ago
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    timestamp = one_year_ago.strftime("%Y-%m-%dT%H:%M:%S")
    logging.info(f"Checking for Readwise updates since {timestamp}")

    # Get recently updated documents from Readwise
    documents = get_readwise_documents(timestamp)

    # Get existing Mochi cards
    mochi_cards = get_mochi_cards()
    logging.info(f"Found {len(mochi_cards)} existing cards in Mochi deck")

    # Create a mapping of Readwise URLs to Mochi card IDs
    url_to_card_id = {}
    for card in mochi_cards:
        # Extract URL from card content (assuming it's in the first line)
        try:
            url = card["content"].split("\n")[0].split("](")[1][:-1]
            url_to_card_id[url] = card["id"]
        except:
            continue

    # Process each document
    processed_count = 0
    updated_count = 0
    created_count = 0
    archived_count = 0

    for doc in documents:
        if (doc["parent_id"] is None and 
            doc["category"] == "article"):
            logging.info(f"Processing: {doc['title']}")
            
            processed_count += 1
            card_content = format_card_content(doc)
            
            if doc["url"] in url_to_card_id:
                card_id = url_to_card_id[doc["url"]]
                logging.info(f"Updating existing card for: {doc['title']}")
                
                if doc["location"] == "archive":
                    logging.info(f"Archiving card for: {doc['title']}")
                    update_mochi_card(card_id, archived=True)
                    archived_count += 1
                else:
                    update_mochi_card(card_id, content=card_content)
                    updated_count += 1
                
            elif doc["location"] == "later":
                logging.info(f"Creating new card for: {doc['title']}")
                create_mochi_card(card_content)
                created_count += 1
        else:
            logging.info(f"Skipping: {doc['title']}")
            print(doc["parent_id"], doc["category"])

    logging.info(f"""
Sync complete:
- {processed_count} articles processed
- {updated_count} cards updated
- {created_count} new cards created 
- {archived_count} cards archived""")

if __name__ == "__main__":
    main()