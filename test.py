from tabpy_client.client import Client

client = Client('http://localhost:9004')   # adjust URL if TabPy is elsewhere

# test inputs: numbers, None, and a string price example
test_prices = [120, 45, None, "$200"]
# threshold used when deploying default is 100 (we deployed is_high_price with default threshold)
resp = client.query('is_high_price', test_prices, 100)
print("response:", resp['response'])