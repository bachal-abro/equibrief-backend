import requests

def call_tweet_endpoint(symbol="AAPL"):
    url = "http://127.0.0.1:8000/"
    params = {"symbol": symbol}

    try:
        print(f"Sending request to tweet about {symbol}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("Server responded:")
        print(response.json())  # Your server must return something
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    call_tweet_endpoint("AAPL")  # Change to "TSLA" etc. as needed
