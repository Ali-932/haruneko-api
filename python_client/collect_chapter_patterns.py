"""
Script to collect chapter title patterns from multiple manga sources
This will help determine the best way to parse chapter numbers from titles
"""
import json
import time
import requests
from typing import Dict, List, Optional
from pathlib import Path


class ChapterPatternCollector:
    """Collect chapter title patterns from various manga sources"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.collected_data = []

    def _request_with_retry(self, request_func, max_retries: int = 5, initial_delay: float = 2.0):
        """Execute request with retry logic"""
        delay = initial_delay
        last_error = None

        for attempt in range(max_retries):
            try:
                return request_func()
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code in [429, 500, 502, 503, 504]:
                    last_error = e
                    if attempt < max_retries - 1:
                        print(f"[WARN] HTTP {e.response.status_code} - Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise
                else:
                    raise
            except (requests.ConnectionError, requests.Timeout) as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"[WARN] {type(e).__name__} - Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise

        if last_error:
            raise last_error

    def get_all_manga(self, source: str, limit: int = 500) -> List[Dict]:
        """
        Fetch all manga from a source using pagination

        Args:
            source: Source identifier
            limit: Maximum number of manga to fetch

        Returns:
            List of manga dictionaries
        """
        print(f"[INFO] Fetching manga list from {source}...")
        all_manga = []
        page = 1
        page_limit = 20

        while True:
            try:
                def _make_request():
                    url = f"{self.base_url}/api/v1/sources/{source}/manga"
                    resp = self.session.get(
                        url,
                        params={'page': page, 'limit': page_limit},
                        timeout=30
                    )
                    resp.raise_for_status()
                    return resp

                resp = self._request_with_retry(_make_request)
                data = resp.json()

                if not data.get('success', False):
                    print(f"[ERROR] API returned error: {data.get('error', 'Unknown error')}")
                    break

                manga_list = data.get('data', [])

                if not manga_list:
                    print(f"[INFO] Reached end of manga list at page {page}")
                    break

                all_manga.extend(manga_list)
                print(f"  Page {page}: fetched {len(manga_list)} manga (total: {len(all_manga)})")

                # Check if we've reached the limit
                if len(all_manga) >= limit:
                    print(f"[INFO] Reached limit of {limit} manga")
                    all_manga = all_manga[:limit]
                    break

                # Check if there are more pages
                meta = data.get('meta', {})
                total_pages = meta.get('totalPages', 0)

                if page >= total_pages:
                    print(f"[INFO] Fetched all {len(all_manga)} manga from {total_pages} pages")
                    break

                page += 1
                time.sleep(0.3)  # Rate limiting

            except Exception as e:
                print(f"[ERROR] Error fetching page {page}: {e}")
                break

        return all_manga

    def search_manga(self, query: str, source: str) -> List[Dict]:
        """Search for manga by title"""
        def _make_request():
            resp = self.session.get(
                f"{self.base_url}/api/v1/sources/{source}/search",
                params={"q": query},
                timeout=30
            )
            resp.raise_for_status()
            return resp

        try:
            resp = self._request_with_retry(_make_request)
            data = resp.json()

            if isinstance(data, dict) and data.get('success'):
                return data.get('data', [])
            elif isinstance(data, list):
                return data

            return []
        except Exception as e:
            print(f"[ERROR] Search failed for '{query}' on {source}: {e}")
            return []

    def fetch_chapters(self, manga_id: str, source: str) -> List[Dict]:
        """Fetch chapter list for a manga"""
        def _make_request():
            encoded_manga_id = requests.utils.quote(manga_id, safe='')
            resp = self.session.get(
                f"{self.base_url}/api/v1/sources/{source}/manga/{encoded_manga_id}/chapters",
                timeout=30
            )
            resp.raise_for_status()
            return resp

        try:
            resp = self._request_with_retry(_make_request)
            data = resp.json()

            if isinstance(data, dict) and data.get('success'):
                return data.get('data', [])
            elif isinstance(data, list):
                return data

            return []
        except Exception as e:
            print(f"[ERROR] Failed to fetch chapters for {manga_id}: {e}")
            return []

    def collect_from_manga_list(self, source: str, manga_list: List[Dict], chapters_per_manga: int = 3) -> int:
        """
        Collect chapter patterns from a list of manga

        Args:
            source: Source identifier
            manga_list: List of manga dictionaries from API
            chapters_per_manga: Number of chapters to collect per manga

        Returns:
            Number of manga successfully collected
        """
        collected_count = 0

        print(f"\n{'='*70}")
        print(f"Processing {len(manga_list)} manga from {source}")
        print(f"{'='*70}")

        for idx, manga in enumerate(manga_list, 1):
            try:
                manga_id = manga.get('id')
                manga_title = manga.get('title')

                if not manga_id:
                    print(f"[{idx}/{len(manga_list)}] [SKIP] No manga ID")
                    continue

                print(f"\n[{idx}/{len(manga_list)}] Processing: {manga_title}")
                print(f"  ID: {manga_id}")

                # Fetch chapters
                chapters = self.fetch_chapters(manga_id, source)
                if not chapters:
                    print(f"  [SKIP] No chapters found")
                    continue

                print(f"  [INFO] Found {len(chapters)} chapters")

                # Collect first N chapters
                sample_chapters = chapters[:chapters_per_manga]

                chapter_data = {
                    "source": source,
                    "manga_id": manga_id,
                    "manga_title": manga_title,
                    "total_chapters": len(chapters),
                    "sample_chapters": []
                }

                for i, chapter in enumerate(sample_chapters, 1):
                    chapter_info = {
                        "index": i,
                        "id": chapter.get('id'),
                        "title": chapter.get('title', ''),
                        "full_chapter_data": chapter
                    }
                    chapter_data["sample_chapters"].append(chapter_info)
                    print(f"    [{i}] {chapter.get('title', 'NO TITLE')}")

                self.collected_data.append(chapter_data)
                collected_count += 1

                # Rate limiting - be nice to the API
                time.sleep(0.5)

            except Exception as e:
                print(f"  [ERROR] Failed to process: {e}")
                continue

        return collected_count

    def save_results(self, output_file: str = "chapter_patterns.json"):
        """Save collected data to JSON file"""
        output_path = Path(output_file)

        with output_path.open('w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*70}")
        print(f"RESULTS SAVED")
        print(f"{'='*70}")
        print(f"File: {output_path.absolute()}")
        print(f"Total manga collected: {len(self.collected_data)}")

        # Count total chapters
        total_chapters = sum(len(m["sample_chapters"]) for m in self.collected_data)
        print(f"Total chapters collected: {total_chapters}")

        # Show sample of titles
        print(f"\n{'='*70}")
        print("SAMPLE CHAPTER TITLES")
        print(f"{'='*70}")
        for manga in self.collected_data[:5]:
            print(f"\nManga: {manga['manga_title']} (source: {manga['source']})")
            for ch in manga["sample_chapters"]:
                print(f"  - {ch['title']}")


def main():
    """Main collection script"""

    print("="*70)
    print("CHAPTER PATTERN COLLECTION SCRIPT")
    print("="*70)
    print(f"Source: mangahere only")
    print(f"Chapters per manga: 3")
    print("="*70)

    collector = ChapterPatternCollector()

    # Use only mangahere source
    source = "mangahere"
    print(f"\n[INFO] Using source: {source}")

    # Fetch manga list from source
    manga_limit = 200
    manga_list = collector.get_all_manga(source, limit=manga_limit)

    if not manga_list:
        print("[ERROR] No manga found!")
        return

    print(f"\n[INFO] Fetched {len(manga_list)} manga from {source}")
    print(f"[INFO] Expected total chapters: ~{len(manga_list) * 3}")

    # Collect chapter data from manga list
    total_collected = collector.collect_from_manga_list(source, manga_list, chapters_per_manga=3)

    # Save results
    collector.save_results("chapter_patterns.json")

    print(f"\n{'='*70}")
    print("COLLECTION COMPLETE")
    print(f"{'='*70}")
    print(f"Total manga collected: {total_collected}")
    print(f"Output file: chapter_patterns.json")
    print(f"\nNext steps:")
    print(f"1. Review the chapter_patterns.json file")
    print(f"2. Analyze the patterns to determine best parsing strategy")
    print(f"3. Update the resolve_chapter() method accordingly")


if __name__ == "__main__":
    main()
