from tabpy_client.client import Client

def is_high_price(prices, threshold=100):
    """
    Return a list of booleans: True if price > threshold, False otherwise.
    Handles None and string prices like "$1,200".
    """
    return [
        False
        if p is None
        else float(str(p).replace('$', '').replace(',', '')) > threshold
        for p in prices
    ]


def property_category(prices):
    """
    Categorize price into Budget / Mid-range / High-end / Luxury.
    Returns 'Unknown' for None or malformed prices.
    """
    out = []
    for p in prices:
        if p is None:
            out.append('Unknown')
            continue
        try:
            v = float(str(p).replace('$', '').replace(',', ''))
        except Exception:
            out.append('Unknown')
            continue

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
    """
    Compute price divided by number of reviews.
    If reviews == 0 or missing, returns 0.0 for that item.
    """
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
    """
    Map availability (0-365 days) to an integer score 1-5.
    0 days -> 1, 365 days -> 5, scaled and rounded for in-between values.
    """
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