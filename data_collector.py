import requests
import requests.auth
import json


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


def data_collector():
    # Get credentials
    creds = credentials_reader()
    print(creds)

    # Authenticate with the reddit api
    auth = get_auth(creds)
    print(auth)

    # Get saved posts
    json = get_saved_json(creds, auth)
    print(json)


if __name__ == "__main__":
    data_collector()
