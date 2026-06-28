from urllib.request import Request, urlopen
from constants import WEB_FETCH_TIMEOUT_SECONDS, WEB_FETCH_USER_AGENT


def fetch_page_text(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": WEB_FETCH_USER_AGENT},
    )
    try:
        with urlopen(request, timeout=WEB_FETCH_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception:
        return ""
