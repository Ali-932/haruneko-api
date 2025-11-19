#!/usr/bin/env python3
"""
Simple Example - Basic usage of HaruNeko Download Service

⚠️  IMPORTANT: Start the HaruNeko API server FIRST!
    cd .. && npm run dev

Then verify it's running at: http://localhost:3000/api-docs
"""

from haruneko_download_service import HaruNekoDownloadService


def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         HaruNeko API Client - Simple Example                    ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # Initialize service
    service = HaruNekoDownloadService(
        base_url="http://localhost:3000/api/v1",
        download_root="downloads"
    )

    # Configuration
    source_id = "mangadex"
    search_query = "one piece"

    print(f"Source: {source_id}")
    print(f"Search: {search_query}")
    print("-" * 70)

    # Step 1: Search for manga
    print("\n[1] Searching for manga...")
    results = service.search_manga(source_id, search_query, page=1, limit=5)

    if not results:
        print("❌ No manga found!")
        return

    print(f"✓ Found {len(results)} results")

    # Step 2: Select first result
    manga = results[0]
    manga_id = manga["id"]
    manga_title = manga.get("title", "Unknown")

    print(f"\n[2] Selected: {manga_title}")

    # Step 3: Get chapters
    print(f"\n[3] Fetching chapters...")
    chapters = service.fetch_chapters(source_id, manga_id)

    if not chapters:
        print("❌ No chapters found!")
        return

    print(f"✓ Found {len(chapters)} chapters")
    print(f"First chapter: {chapters[0].get('title', 'Unknown')}")

    # Step 4: Download first chapter (commented out by default)
    print(f"\n[4] Download example (uncomment to actually download)")
    print(f"To download, uncomment the code below in the script")

    # Uncomment to actually download:
    # chapter_ids = [chapters[0]["id"]]
    # result = service.download_chapters(
    #     source_id=source_id,
    #     manga_id_raw=manga_id,
    #     chapter_ids=chapter_ids,
    #     format="cbz",
    #     options={"quality": "high", "includeMetadata": True}
    # )
    #
    # if result["success"]:
    #     download_id = result["response"]["data"]["id"]
    #     print(f"✓ Download started! ID: {download_id}")
    #     print(f"Check status: GET /api/v1/downloads/{download_id}")
    # else:
    #     print(f"❌ Download failed: {result['error']}")

    print("\n" + "=" * 70)
    print("✓ Example complete!")
    print("\nNext steps:")
    print("1. Check out discover_and_download.py for interactive usage")
    print("2. Read README.md for complete documentation")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except ConnectionError as e:
        print("\n❌ ERROR: Could not connect to API server!")
        print("\nMake sure the HaruNeko API server is running:")
        print("  $ cd .. && npm run dev")
        print("\nThen verify at: http://localhost:3000/api-docs")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
