"""
HaruNeko Download Service - Download manga chapters via HaruNeko API
"""
import json
import time
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests


class HaruNekoDownloadService:
    """Service for downloading manga chapters via HaruNeko API"""

    def __init__(
        self,
        base_url: str = "http://localhost:3000/api/v1",
        download_root: str = "downloads",
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.download_root = Path(download_root)
        self.download_root.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def _request_with_retry(
        self,
        request_func,
        max_retries: int = 10,
        initial_delay: float = 3.0
    ):
        """
        Execute a request function with retry logic for 429 errors

        Args:
            request_func: Function that makes the HTTP request
            max_retries: Maximum number of retry attempts (default: 10)
            initial_delay: Initial delay in seconds, doubles with each retry (default: 3s)

        Returns:
            Response from the request

        Raises:
            requests.HTTPError: If non-429 error or max retries exceeded
        """
        delay = initial_delay
        last_error = None

        for attempt in range(max_retries):
            try:
                return request_func()
            except requests.HTTPError as e:
                # Check if it's a 429 Too Many Requests error
                if e.response is not None and e.response.status_code == 429:
                    last_error = e
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        print(
                            f"[WARN] 429 Too Many Requests - Retrying in {delay}s "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(delay)
                        delay *= 2  # Double the delay for next retry
                    else:
                        print(
                            f"[ERROR] 429 Too Many Requests - "
                            f"Max retries ({max_retries}) exceeded"
                        )
                        raise
                else:
                    # For non-429 errors, raise immediately
                    raise
            except Exception:
                # For non-HTTP errors, raise immediately
                raise

        # If we get here, all retries failed with 429
        if last_error:
            raise last_error

    # 1. Search --------------------------------------------------------------
    def search_manga(
        self,
        source_id: str,
        query: str,
        page: int = 1,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search for manga by title with retry logic for 429 errors

        Args:
            source_id: The manga source ID (e.g., "mangahere")
            query: Search query string
            page: Page number (default: 1)
            limit: Results per page (default: 100)

        Returns:
            List of manga search results
        """
        def _make_request():
            url = f"{self.base_url}/sources/{source_id}/search"
            params = {"page": page, "limit": limit, "q": query}
            resp = self.session.get(url, params=params, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp

        resp = self._request_with_retry(_make_request)
        return resp.json().get("data", [])

    def resolve_manga_id(
        self,
        source_id: str,
        query: str,
        post: str,
        slug: str,
        max_pages: int = 5
    ) -> Optional[Dict]:
        """
        Find manga by exact match on post + slug

        Args:
            source_id: The manga source ID
            query: Search query string
            post: Expected post ID
            slug: Expected slug
            max_pages: Maximum pages to search (default: 5)

        Returns:
            Matched manga dict or None
        """
        page = 1
        limit = 100

        while page <= max_pages:
            print(f"[INFO] Searching page {page} for {query}...")
            results = self.search_manga(source_id, query, page, limit)

            # Find manga by post + slug
            for item in results:
                try:
                    mid = json.loads(item["id"])
                except (KeyError, json.JSONDecodeError):
                    continue

                if mid.get("post") == post and mid.get("slug") == slug:
                    print(f"[INFO] Found exact match: {item.get('title', 'Unknown')}")
                    return item

            # Check if we've exhausted results
            if len(results) < limit:
                break

            page += 1
            time.sleep(0.5)  # Small delay between pages

        return None

    # 2. Manga Details -------------------------------------------------------
    def get_manga_details(
        self,
        source_id: str,
        manga_id_raw: str
    ) -> Optional[Dict]:
        """
        Get detailed manga information

        Args:
            source_id: The manga source ID
            manga_id_raw: Raw manga ID (JSON string)

        Returns:
            Manga details dict or None
        """
        manga_id_encoded = urllib.parse.quote(manga_id_raw, safe="")

        def _make_request():
            url = f"{self.base_url}/sources/{source_id}/manga/{manga_id_encoded}"
            resp = self.session.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp

        try:
            resp = self._request_with_retry(_make_request)
            return resp.json()
        except requests.HTTPError as e:
            print(f"[ERROR] Failed to get manga details: {e}")
            return None

    # 3. Chapter list --------------------------------------------------------
    def fetch_chapters(
        self,
        source_id: str,
        manga_id_raw: str
    ) -> List[Dict]:
        """
        Fetch all chapters for a manga

        Args:
            source_id: The manga source ID
            manga_id_raw: Raw manga ID (JSON string)

        Returns:
            List of chapter dicts
        """
        manga_id_encoded = urllib.parse.quote(manga_id_raw, safe="")

        def _make_request():
            url = f"{self.base_url}/sources/{source_id}/manga/{manga_id_encoded}/chapters"
            resp = self.session.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp

        try:
            resp = self._request_with_retry(_make_request)
            data = resp.json()
            return data.get("data", [])
        except requests.HTTPError as e:
            print(f"[ERROR] Failed to fetch chapters: {e}")
            return []

    # 4. Validation ----------------------------------------------------------
    def validate_manga_has_chapters(
        self,
        source_id: str,
        manga_title: str,
        post: str,
        slug: str,
        chapter_ids: List[str]
    ) -> Dict:
        """
        Validate that a manga has ALL the required chapters

        Args:
            source_id: The manga source ID
            manga_title: Name of the manga
            post: Expected post ID
            slug: Expected slug
            chapter_ids: List of chapter IDs to validate

        Returns:
            Dict with success, manga_id, manga_title, and missing_chapters
        """
        try:
            # Search for manga (exact match on post + slug)
            chosen_manga = self.resolve_manga_id(source_id, manga_title, post, slug)
            if not chosen_manga:
                return {
                    "success": False,
                    "manga_id": None,
                    "manga_title": None,
                    "missing_chapters": chapter_ids,
                    "error": (
                        f"Manga '{manga_title}' not found with "
                        f"post={post} slug={slug}"
                    )
                }

            manga_id_raw = chosen_manga["id"]
            manga_title_resolved = chosen_manga.get("title", "Unknown")

            # Fetch chapter list
            chapters = self.fetch_chapters(source_id, manga_id_raw)

            if not chapters:
                return {
                    "success": False,
                    "manga_id": manga_id_raw,
                    "manga_title": manga_title_resolved,
                    "missing_chapters": chapter_ids,
                    "error": "Could not fetch any chapters for this manga"
                }

            # Build set of available chapter IDs
            available_chapter_ids = set()
            for chapter in chapters:
                try:
                    chapter_id = json.loads(chapter["id"])
                    # Store the full chapter ID dict as JSON string for comparison
                    available_chapter_ids.add(json.dumps(chapter_id, sort_keys=True))
                except (KeyError, json.JSONDecodeError):
                    continue

            # Check which chapters are missing
            missing_chapters = []
            for chapter_id in chapter_ids:
                # Normalize the chapter ID for comparison
                try:
                    if isinstance(chapter_id, str):
                        # Try to parse if it's a JSON string
                        chapter_obj = json.loads(chapter_id)
                        normalized = json.dumps(chapter_obj, sort_keys=True)
                    else:
                        normalized = json.dumps(chapter_id, sort_keys=True)
                except (json.JSONDecodeError, TypeError):
                    # Treat as simple string
                    normalized = chapter_id

                if normalized not in available_chapter_ids:
                    missing_chapters.append(chapter_id)

            if missing_chapters:
                return {
                    "success": False,
                    "manga_id": manga_id_raw,
                    "manga_title": manga_title_resolved,
                    "missing_chapters": missing_chapters,
                    "error": f"Missing chapters: {missing_chapters}"
                }

            # All chapters found!
            return {
                "success": True,
                "manga_id": manga_id_raw,
                "manga_title": manga_title_resolved,
                "missing_chapters": [],
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "manga_id": None,
                "manga_title": None,
                "missing_chapters": chapter_ids,
                "error": str(e)
            }

    # 5. Download ------------------------------------------------------------
    def download_chapters(
        self,
        source_id: str,
        manga_id_raw: str,
        chapter_ids: List[str],
        format: str = "images",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Download multiple chapters

        Args:
            source_id: The manga source ID
            manga_id_raw: Raw manga ID (JSON string)
            chapter_ids: List of chapter IDs to download
            format: Download format (images, cbz, pdf, epub)
            options: Additional download options

        Returns:
            Dict with success status and download info
        """
        if options is None:
            options = {
                "quality": "low",
                "includeMetadata": True,
            }

        payload = {
            "sourceId": source_id,
            "mangaId": manga_id_raw,
            "chapterIds": chapter_ids,
            "format": format,
            "options": options,
        }

        def _make_request():
            url = f"{self.base_url}/downloads"
            resp = self.session.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            return resp

        try:
            resp = self._request_with_retry(_make_request)
            result = resp.json()

            return {
                "success": True,
                "error": None,
                "response": result,
                "status_code": resp.status_code
            }

        except requests.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "response": None,
                "status_code": e.response.status_code if e.response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "status_code": None
            }

    def validate_and_download(
        self,
        source_id: str,
        manga_title: str,
        post: str,
        slug: str,
        chapter_ids: List[str],
        format: str = "images",
        options: Optional[Dict[str, Any]] = None,
        validate_only: bool = False
    ) -> Dict:
        """
        Main method: Validate chapters exist, then download them

        Args:
            source_id: The manga source ID
            manga_title: Name of the manga
            post: Expected post ID
            slug: Expected slug
            chapter_ids: List of chapter IDs to download
            format: Download format (default: images)
            options: Additional download options
            validate_only: Only validate, don't download (dry-run)

        Returns:
            Dict with success status, validation results, and download info
        """
        print(f"\n{'='*60}")
        print(f"VALIDATING: {manga_title}")
        print(f"Source: {source_id}")
        print(f"Post: {post}, Slug: {slug}")
        print(f"Chapters to check: {len(chapter_ids)}")
        print(f"{'='*60}\n")

        # Step 1: Validate
        validation = self.validate_manga_has_chapters(
            source_id, manga_title, post, slug, chapter_ids
        )

        if not validation["success"]:
            print(f"\n[ERROR] Validation failed: {validation['error']}")
            return {
                "success": False,
                "validation": validation,
                "download": None
            }

        print(f"\n[SUCCESS] All {len(chapter_ids)} chapters found!")

        if validate_only:
            print("\n[INFO] Validation-only mode - skipping download")
            return {
                "success": True,
                "validation": validation,
                "download": None
            }

        # Step 2: Download
        print(f"\n{'='*60}")
        print(f"DOWNLOADING: {validation['manga_title']}")
        print(f"Chapters: {len(chapter_ids)}")
        print(f"Format: {format}")
        print(f"{'='*60}\n")

        download_result = self.download_chapters(
            source_id,
            validation["manga_id"],
            chapter_ids,
            format,
            options
        )

        if download_result["success"]:
            print(f"\n[SUCCESS] Download request completed!")
            print(f"Response: {json.dumps(download_result['response'], indent=2)}")
        else:
            print(f"\n[ERROR] Download failed: {download_result['error']}")

        return {
            "success": download_result["success"],
            "validation": validation,
            "download": download_result
        }
