import requests
import requests.auth
import json
import pandas as pd


def credentials_reader():
    return json.load(open("credentials.json"))


def get_auth(creds):
    client_auth = requests.auth.HTTPBasicAuth(creds.get("clientID"), creds.get("clientSecret"))
    post_data = {"grant_type": "password", "username": creds.get("username"), "password": creds.get("password")}
    headers = {"User-Agent": "Reddit_explorer by %s" % creds.get("username")}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data,
                             headers=headers)
    return response.json()


def get_saved_json(creds, auth):
    headers = {"Authorization": "bearer %s" % auth.get("access_token"),
               "User-Agent": "Reddit_explorer by %s" % creds.get("username")}
    response = requests.get("https://oauth.reddit.com/user/%s/saved" % creds.get("username"), headers=headers)
    return response.json()


def post_extractor(raw):
    children = raw.get("data").get("children")
    children = [i.get("data") for i in children]

    columns = ["created", "author", "num_comments", "over_18", "permalink", "score", "subreddit", "title"]
    df = pd.DataFrame(children)[columns]

    return df


def data_collector():
    # Get credentials
    creds = credentials_reader()
    print(creds)

    # Authenticate with the reddit api
    auth = get_auth(creds)
    print(auth)

    # Get raw saved
    raw = get_saved_json(creds, auth)
    print(raw)

    # Get posts
    posts = post_extractor(raw)

    # Write posts to file
    posts.to_csv("saved_posts.csv", index=False)


if __name__ == "__main__":
    data_collector()
