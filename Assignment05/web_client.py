import requests
import json

def handle_status_code(response):
    if response.status_code == 200 or response.status_code == 201:
        print(f"Success! Status code: {response.status_code}")
    elif response.status_code == 404:
        print("Error: 404 Not Found")
    elif response.status_code == 500:
        print("Error: 500 Internal Server Error")
    else:
        print(f"Received status code: {response.status_code}")

def make_get_request():
    url = "https://jsonplaceholder.typicode.com/posts"
    print("\nMaking GET request...\n")

    try:
        response = requests.get(url)
        handle_status_code(response)

        if response.status_code == 200:
            data = response.json()
            print("\nPost Titles:\n")
            for post in data:
                print(f"- {post['title']}")
    except requests.exceptions.RequestException as e:
        print(f"Network error during GET request: {e}")

def make_post_request():
    url = "https://jsonplaceholder.typicode.com/posts"
    payload = {
        "title": "My Sample Post",
        "body": "This is a test post from my Python web client.",
        "userId": 1
    }

    print("\nMaking POST request...\n")

    try:
        response = requests.post(url, json=payload)
        handle_status_code(response)

        print("\nServer Response:\n")
        print(json.dumps(response.json(), indent=4))
    except requests.exceptions.RequestException as e:
        print(f"Network error during POST request: {e}")

def test_error_handling():
    bad_url = "https://jsonplaceholder.typicode.com/invalidendpoint"
    print("\nTesting error handling with a bad URL...\n")

    try:
        response = requests.get(bad_url)
        handle_status_code(response)
    except requests.exceptions.RequestException as e:
        print(f"Network error during error-handling test: {e}")

def main():
    print("=== Python Web Client ===")
    make_get_request()
    make_post_request()
    test_error_handling()

if __name__ == "__main__":
    main()