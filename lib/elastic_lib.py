from elasticsearch import Elasticsearch, helpers
from datetime import datetime


def connect_to_elastic(host_ip, username, password):
    es = Elasticsearch(
        hosts=[host_ip], http_auth=(username, password), verify_certs=False
    )

    return es


def write_to_elastic(
    es,
    tag,
    title=None,
    date=None,
    content=None,
    link=None,
    video_title=None,
    all_usernames=None,
    all_comments=None,
    author=None,
    avatar=None,
    all_status=None,
):
    if tag == "news":
        actions = [
            {
                "_index": "news",
                "_id": f"{title}",
                "_source": {
                    "date": date,
                    "title": title,
                    "content": content,
                    "link": link,
                },
            }
        ]
        # Use the helpers library to bulk import
        try:
            response = helpers.bulk(es, actions, chunk_size=500)
            print(f"\nSuccessfully indexed {len(actions)} documents to index 'news'.\n")
            print(response)
        except Exception as e:
            print(f"\nError indexing data: {e}\n")

    elif tag == "eksi":
        actions = [
            {
                "_index": "eksi",
                "_id": f"{date_i}-{author_i}",
                "_source": {
                    "date": date_i,
                    "author": author_i,
                    "title": title_i,
                    "avatar": avatar_i,
                    "content": content_i,
                },
            }
            for i, (date_i, author_i, title_i, avatar_i, content_i) in enumerate(
                zip(date, author, title, avatar, content)
            )
        ]
        # Use the helpers library to bulk import
        try:
            response = helpers.bulk(es, actions, chunk_size=500)
            print(f"\nSuccessfully indexed {len(actions)} documents to index 'eksi'.\n")
            print(response)
        except Exception as e:
            print(f"\nError indexing data: {e}\n")

    elif tag == "youtube":
        actions = [
            {
                "_index": "youtube_yorumlar",
                "_id": f"{title}-{i}",
                "_source": {
                    "video_baslik": video_title,
                    "kul_lanci": username.text,
                    "yorum": comment.text,
                    "durum": status
                },
            }
            for i, (username, comment, status) in enumerate(zip(all_usernames, all_comments, all_status))
        ]

        # Use the helpers library to bulk import
        try:
            response = helpers.bulk(es, actions, chunk_size=500)
            print(
                f"\nSuccessfully indexed {len(actions)} documents to index 'youtube_yorumlar'.\n"
            )
        except Exception as e:
            print(f"\nError indexing data: {e}\n")


    else:
        raise ValueError("Invalid tag")
