import os
import requests
import re

from flask import redirect, render_template, request, session
from functools import wraps
from dateutil import parser

from ratelimit import limits, sleep_and_retry

#define 5 minutes for the ratelimit
FIVE_MINUTES = 300

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#decorate domain_search function with rate limit and ability to sleep and retry if limit has been reached
@sleep_and_retry
@limits(calls=1200, period=FIVE_MINUTES)
def domain_search(domain):
    """Seach for domain availability."""

    # Contact API
    try:
        api_email = os.getenv("API_EMAIL")
        api_key = os.getenv("API_KEY")
        api_id = os.getenv("API_ACCOUNT_ID")

        headers = {
            "X-Auth-Email": f"{api_email}",
            "X-Auth-Key": f"{api_key}",
            "Content-Type": "application/json"
            }

        url = f"https://api.cloudflare.com/client/v4/accounts/{api_id}/registrar/domains/{domain}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

    except requests.RequestException:
        return None

    # Parse response
    try:
        domain = response.json()

        if domain["result"]["available"]:
            return {
                "name": domain["result"]["name"],
                "available": domain["result"]["available"]
            }
        else:
            return {
                "name": domain["result"]["name"],
                "available": domain["result"]["available"],
                "expires_at": parser.parse(domain["result"]["expires_at"]).date(),
                "registry_statuses": domain["result"]["registry_statuses"]
            }
    except (KeyError, TypeError, ValueError):
        return None


def validate(password):
    """Validate password with regex"""

    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,32}$"

    if (re.search(reg, password)):
        return True
    return False

def is_domain(domain):
    """Validate domain with regex"""

    #reg to allow both just domain name (with no .com at the end) and also domain with .com at the end
    #reg = "^(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-))+(?:\.com|\.org|\.net|\.io|\.co|)$"

    reg = "^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?:com|org|net|io|co)$"

    if (re.search(reg, domain)):
        return True
    return False

vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

# Generate 5 character words according to the most common 13 patterns (94.4% coverage)
def generate_5char_words():
    words = []

    # Generate the cvcvc pattern (25% of english 5 letter words)

    for c1 in consonants:
        for v1 in vowels:
            for c2 in consonants:
                for v2 in vowels:
                    for c3 in consonants:
                        word = c1 + v1 + c2 + v2 + c3
                        words.append(word)

    # Generate the cvccc pattern (16% of english 5 letter words)

    for c1 in consonants:
        for v1 in vowels:
            for c2 in consonants:
                for c3 in consonants:
                    for c4 in consonants:
                        word = c1 + v1 + c2 + c3 + c4
                        words.append(word)

    # Generate the ccvcc pattern (11% of english 5 letter words)

    for c1 in consonants:
        for c2 in consonants:
            for v1 in vowels:
                for c3 in consonants:
                    for c4 in consonants:
                        word = c1 + c2 + v1 + c3 + c4
                        words.append(word)

    # Generate the cvccv pattern (9% of english 5 letter words)

    for c1 in consonants:
        for v1 in vowels:
            for c2 in consonants:
                for c3 in consonants:
                    for v2 in vowels:
                        word = c1 + v1 + c2 + c3 + v2
                        words.append(word)

    # Generate the cvvcc pattern (9% of english 5 letter words)

    for c1 in consonants:
        for v1 in vowels:
            for v2 in vowels:
                for c2 in consonants:
                    for c3 in consonants:
                        word = c1 + v1 + v2 + c2 + c3
                        words.append(word)

    # Generate the vccvc pattern (5% of english 5 letter words)

    for v1 in vowels:
        for c1 in consonants:
            for c2 in consonants:
                for v2 in vowels:
                    for c3 in consonants:
                        word = v1 + c1 + c2 + v2 + c3
                        words.append(word)

    # Generate the ccvvc pattern (4% of english 5 letter words)

    for c1 in consonants:
        for c2 in consonants:
            for v1 in vowels:
                for v2 in vowels:
                    for c3 in consonants:
                        word = c1 + c2 + v1 + v2 + c3
                        words.append(word)

    # Generate the ccvcv pattern (4% of english 5 letter words)

    for c1 in consonants:
        for c2 in consonants:
            for v1 in vowels:
                for c3 in consonants:
                    for v2 in vowels:
                        word = c1 + c2 + v1 + c3 + v2
                        words.append(word)

    # Generate the cvvcv pattern (3% of english 5 letter words)

    for c1 in consonants:
        for v1 in vowels:
            for v2 in vowels:
                for c2 in consonants:
                    for v3 in vowels:
                        word = c1 + v1 + v2 + c2 + v3
                        words.append(word)

    # Generate the vcvcc pattern (2% of english 5 letter words)

    for v1 in vowels:
        for c1 in consonants:
            for v2 in vowels:
                for c2 in consonants:
                    for c3 in consonants:
                        word = v1 + c1 + v2 + c2 + c3
                        words.append(word)

    # Generate the cvcvv pattern (2% of english 5 letter words)

    for c1 in consonants:
        for v1 in vowels:
            for c2 in consonants:
                for v2 in vowels:
                    for v3 in vowels:
                        word = c1 + v1 + c2 + v2 + v3
                        words.append(word)

    # Generate the cccvc pattern (2% of english 5 letter words)

    for c1 in consonants:
        for c2 in consonants:
            for c3 in consonants:
                for v1 in vowels:
                    for c4 in consonants:
                        word = c1 + c2 + c3 + v1 + c4
                        words.append(word)


    # Generate the vcvcv pattern (2% of english 5 letter words)

    for v1 in vowels:
        for c1 in consonants:
            for v2 in vowels:
                for c2 in consonants:
                    for v3 in vowels:
                        word = v1 + c1 + v2 + c2 + v3
                        words.append(word)

    return words