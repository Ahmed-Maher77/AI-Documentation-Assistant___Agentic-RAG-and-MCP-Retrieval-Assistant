import urllib.request
from bs4 import BeautifulSoup
from langchain.tools import tool


@tool
def fetch_up_to_date_doc(url: str) -> str:
    """Fetch real-time, up-to-date documentation content directly from a web URL or raw markdown via llms.txt endpoint."""
    try:
        target_url = url
        # Auto-try .md variant for docs.langchain.com URLs if not specified
        if "docs.langchain.com" in url and not (url.endswith(".md") or url.endswith(".txt") or url.endswith(".html")):
            target_url = f"{url.rstrip('/')}.md"

        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                if target_url.endswith(".md") or target_url.endswith(".txt"):
                    return f"Source: {target_url}\n\n{content[:4000]}"

                soup = BeautifulSoup(content, "html.parser")
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.extract()

                text = soup.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return f"Source: {url}\n\n" + "\n".join(lines[:150])[:4000]
        except Exception:
            # Fallback to original URL
            req_orig = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req_orig, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                soup = BeautifulSoup(html, "html.parser")

                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.extract()

                text = soup.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return f"Source: {url}\n\n" + "\n".join(lines[:150])[:4000]
    except Exception as exc:
        return f"Failed to fetch up-to-date doc from {url}: {exc}"
