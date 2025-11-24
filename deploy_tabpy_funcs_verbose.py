import time
import json
import requests
from tabpy_client.client import Client

TABPY_URL = "http://localhost:9004"
POLL_TIMEOUT = 60
POLL_INTERVAL = 1

# --- Function definitions ---
def is_high_price(prices, threshold=100):
    return [
        False
        if p is None
        else float(str(p).replace('$', '').replace(',', '')) > threshold
        for p in prices
    ]

def property_category(prices):
    out = []
    for p in prices:
        if p is None:
            out.append('Unknown'); continue
        try:
            v = float(str(p).replace('$', '').replace(',', ''))
        except Exception:
            out.append('Unknown'); continue
        if v <= 50:
            out.append('Budget')
        elif v <= 100:
            out.append('Mid-range')
        elif v <= 200:
            out.append('High-end')
        else:
            out.append('Luxury')
    return out

def price_per_review(prices, reviews):
    out = []
    for p, r in zip(prices, reviews):
        try:
            price = float(str(p).replace('$', '').replace(',', '')) if p is not None else 0.0
        except Exception:
            price = 0.0
        try:
            rev = float(r) if r is not None else 0.0
        except Exception:
            rev = 0.0
        out.append(price / rev if rev > 0 else 0.0)
    return out

def availability_score(avails):
    out = []
    for a in avails:
        try:
            av = float(a) if a is not None else 0.0
        except Exception:
            av = 0.0
        pct = min(max(av / 365.0, 0.0), 1.0)
        score = int(round(pct * 4)) + 1
        score = max(1, min(5, score))
        out.append(score)
    return out

FUNCTIONS = {
    "is_high_price": (is_high_price, "Return booleans when price > threshold"),
    "property_category": (property_category, "Return category strings for prices"),
    "price_per_review": (price_per_review, "Return price per review"),
    "availability_score": (availability_score, "Return availability 1-5 score"),
}

def get_endpoints():
    try:
        r = requests.get(TABPY_URL.rstrip('/') + '/endpoints', timeout=5)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return r.text
    except Exception as e:
        return {"error": str(e)}

def wait_for_endpoint(name, timeout=POLL_TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        eps = get_endpoints()
        txt = str(eps)
        if name in txt:
            return True, eps
        time.sleep(POLL_INTERVAL)
    return False, get_endpoints()

def main():
    client = Client(TABPY_URL)
    print("TabPy URL:", TABPY_URL)
    print("Existing endpoints (before):")
    print(json.dumps(get_endpoints(), indent=2) if isinstance(get_endpoints(), dict) else get_endpoints())

    for fname, (fobj, fdesc) in FUNCTIONS.items():
        print("\n--- Deploying:", fname, "---")
        try:
            client.deploy(fname, fobj, fdesc, override=True)
        except Exception as ex:
            print("client.deploy raised exception:", repr(ex))
            print("Current endpoints listing:")
            print(json.dumps(get_endpoints(), indent=2) if isinstance(get_endpoints(), dict) else get_endpoints())
            # continue to next to see behavior
            continue

        print("Deploy request sent for", fname, "- polling for registration ({}s)".format(POLL_TIMEOUT))
        ok, eps = wait_for_endpoint(fname)
        if ok:
            print("Endpoint '{}' appears registered.".format(fname))
            print("Endpoints (snippet):")
            try:
                print(json.dumps(eps, indent=2))
            except Exception:
                print(str(eps)[:2000])
        else:
            print("Timed out waiting for endpoint '{}'. Current endpoints:".format(fname))
            try:
                print(json.dumps(eps, indent=2))
            except Exception:
                print(str(eps)[:2000])
            # continue to next function

        # quick trial query to validate runtime response if endpoint present
        try:
            if fname == "is_high_price":
                sample = client.query(fname, [120, 45, None, "$200"], 100)
            elif fname == "property_category":
                sample = client.query(fname, [120, 45, None, "$200"])
            elif fname == "price_per_review":
                sample = client.query(fname, [120, 45, "$200"], [10, 5, 0])
            elif fname == "availability_score":
                sample = client.query(fname, [0, 120, 365, None])
            else:
                sample = None
            print("Trial query result for '{}':".format(fname), sample if sample is None else sample.get('response', sample))
        except Exception as ex:
            print("Trial query for '{}' failed:".format(fname), repr(ex))
            # print endpoints again for context
            print("Endpoints after trial (for debug):")
            print(json.dumps(get_endpoints(), indent=2) if isinstance(get_endpoints(), dict) else get_endpoints())

    print("\nFinished deployment attempts. Final endpoints listing:")
    print(json.dumps(get_endpoints(), indent=2) if isinstance(get_endpoints(), dict) else get_endpoints())

if __name__ == "__main__":
    main()