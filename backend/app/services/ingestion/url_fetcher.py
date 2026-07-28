import httpx

USER_AGENT = "PantryBot/0.1 (+https://github.com/crason-t/Pantry)"


def fetch_html(url: str, timeout: float = 10.0) -> str:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return response.text
