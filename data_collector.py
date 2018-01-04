import requests
import requests.auth
import json
import pandas as pd
import os.path


def credentials_reader():
    return json.load(open("credentials.json"))


def get_auth(creds):
    client_auth = requests.auth.HTTPBasicAuth(creds.get("clientID"), creds.get("clientSecret"))
    post_data = {"grant_type": "password", "username": creds.get("username"), "password": creds.get("password")}
    headers = {"User-Agent": "Reddit_explorer by %s" % creds.get("username")}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data,
                             headers=headers)
    return response.json()


def get_json(creds, auth, before=None, after=None):

    headers = {"Authorization": "bearer %s" % auth.get("access_token"),
               "User-Agent": "Reddit_explorer by %s" % creds.get("username")}

    url = "https://oauth.reddit.com/user/%s/saved?limit=100" % creds.get("username")

    if before:
        url += "&before=" + before

    if after:
        url += "&after=" + after

    response = requests.get(url, headers=headers)
    return response.json()


def post_extractor(raw):
    try:
        children = raw.get("data").get("children")

        # Combine the post kind with the post data
        vals = []
        for i in children:
            a = i.get("data")
            a["kind"] = i.get("kind")
            vals.append(a)

        columns = ["kind", "id", "created", "author", "num_comments", "over_18", "permalink", "score", "subreddit", "title"]
        return pd.DataFrame(vals)[columns]

    except:
        return pd.DataFrame(columns=columns)


def get_posts(creds, auth, before=None, after=None):
    # Get raw data
    raw = get_json(creds, auth, before, after)
    # Process data
    posts = post_extractor(raw)

    return posts


def data_collector():
    # Get credentials
    creds = credentials_reader()
    print(creds)

    # Authenticate with the reddit api
    auth = get_auth(creds)
    print(auth)

    # Check to see if there is already data
    if os.path.exists("./saved_posts.csv"):
        # Get existing dataset
        print("Getting existing dataset")
        data = pd.read_csv("./saved_posts.csv", header=0)

        # Get the id of the top and bottom posts in the dataset
        head = data.head(1)
        head_id = head["kind"].iloc[0] + "_" + head["id"].iloc[0]
        print("Head id: %s" % head_id)
        tail = data.tail(1)
        tail_id = tail["kind"].iloc[0] + "_" + tail["id"].iloc[0]
        print("Tail id: %s" % tail_id)

        # Get the posts from before and after the current dataset
        before = get_posts(creds, auth, before=head_id)
        after = get_posts(creds, auth, after=tail_id)

        # Concatenate back into one dataframe
        data = data.append(after)
        data = before.append(data)

    else:
        data = get_posts(creds, auth)


    # Write posts to file
    data.to_csv("saved_posts.csv", index=False)


if __name__ == "__main__":
    data_collector()
