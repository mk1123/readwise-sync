import datetime
import requests
import os
import json
import pytz

readwise_token = "3lZVLq2HLf27gLCVqTzVTmvlTcmHMXkdxuEeqKraJtHxoYCyyJ"
zettel_folder = os.path.expanduser("~/Dropbox/zettel")

book_id_to_metadata = {}


def fetch_from_highlights_api(updated_after=None):
    full_data = []
    current_page = 1
    while True:
        params = {}
        params["page"] = current_page
        if updated_after:
            params["highlighted_at__gt"] = updated_after
        response = requests.get(
            url="https://readwise.io/api/v2/highlights/",
            params=params,
            headers={"Authorization": f"Token {readwise_token}"},
            verify=False,
        )
        response_json = response.json()
        full_data.extend(response_json["results"])
        if response_json["next"]:
            current_page += 1
        else:
            break
    return full_data


def fetch_book_metadata(book_id):
    if book_id in book_id_to_metadata:
        return book_id_to_metadata[book_id]
    response = requests.get(
        url=f"https://readwise.io/api/v2/books/{book_id}/",
        headers={"Authorization": f"Token {readwise_token}"},
    )
    response_json = response.json()
    # return {
    #     "readable_title": response_json["title"],
    # }
    book_id_to_metadata[book_id] = response_json
    return response_json


def populate_new_article_template(title, source_url, highlighter_url):
    return f"""# {title}

---
source: {source_url}
highlighter_url: {highlighter_url}
tags: #literature #inbox
uid: [[{generate_uuid_from_current_time()}]]
---

"""


def generate_uuid_from_current_time(delta=0):
    return str(
        int(
            datetime.datetime.now(pytz.timezone("US/Pacific")).strftime(
                "%Y%m%d%H%M"
            )
        )
        + delta
    )


def does_file_exist_in_zettel_folder(title):
    for file in os.listdir(zettel_folder):
        if title in file:
            return zettel_folder + "/" + file
    return False


def create_zettel(title, source_url, highlighter_url, idx):
    file_path = (
        zettel_folder
        + "/"
        + generate_uuid_from_current_time(idx)
        + " "
        + title
        + ".md"
    )
    with open(file_path, "w") as f:
        f.write(
            populate_new_article_template(title, source_url, highlighter_url)
        )
    return file_path


def generate_highlight_snippet(highlight_text, comment_text):
    highlight_text_blocks = highlight_text.split("\n")
    cleaned_up_highlighted_text = "\n".join(
        "> " + line for line in highlight_text_blocks if line != ""
    )
    comment_text = "\n\n" + comment_text if comment_text else ""
    return cleaned_up_highlighted_text + comment_text + "\n\n"


def add_highlight_to_zettel(file_path, highlight_text, comment_text):
    with open(file_path, "a") as f:
        f.write(generate_highlight_snippet(highlight_text, comment_text))


if __name__ == "__main__":
    last_fetch_was_at = datetime.datetime.now(pytz.utc) - datetime.timedelta(
        minutes=60
    )  # use your own stored date
    new_data = fetch_from_highlights_api(last_fetch_was_at.isoformat())
    print(json.dumps(new_data, indent=4))
    for idx, book in enumerate(new_data):
        book_id = book["book_id"]
        book_details = fetch_book_metadata(book_id)
        print(book_details)
        # source_url = book["source_url"]
        # highlighter_url = book["unique_url"]
        # file_path = does_file_exist_in_zettel_folder(book_title)
        # if not file_path:
        #     file_path = create_zettel(
        #         book_title, source_url, highlighter_url, idx
        #     )
        # for highlight in book["highlights"]:
        #     text = highlight["text"]
        #     comment = highlight["note"]
        #     add_highlight_to_zettel(file_path, text, comment)
