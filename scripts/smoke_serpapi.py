import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.serpapi.client import SerpApiClient  # noqa: E402


async def main() -> None:
    client = SerpApiClient(os.environ.get("SERPAPI_API_KEY", ""))
    payload = await client.search(
        engine="google_scholar",
        params={
            "q": "neuromorphic computing",
            "as_ylo": 2026,
            "num": 3,
            "hl": "en",
            "json_restrictor": "organic_results[].{title,link,publication_info,cited_by}",
        },
    )

    for item in payload.get("organic_results", []):
        print(item.get("title"))


if __name__ == "__main__":
    asyncio.run(main())
