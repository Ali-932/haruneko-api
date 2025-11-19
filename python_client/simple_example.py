#!/usr/bin/env python3
"""
Simple Example - Download manga chapters with minimal code

Usage:
    1. Start the HaruNeko API: cd .. && npm run dev
    2. Run this script: python simple_example.py
"""

from haruneko_download_service import HaruNekoDownloadService


def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              HaruNeko API - Simple Example                       ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # Initialize service
    service = HaruNekoDownloadService()

    # Example 1: Validate only (check if manga and chapters exist)
    print("\n" + "="*70)
    print("EXAMPLE 1: Validate manga and chapters (dry run)")
    print("="*70)

    result = service.download_manga_chapters(
        source_id="mangadex",
        manga_name="One Piece",
        chapter_numbers=[1, 2, 3],
        validate_only=True  # Just check, don't download
    )

    if result["success"]:
        print("\n✓ Validation successful!")
        print(f"  Manga: {result['manga']['title']}")
        print(f"  Chapters found: {len(result['chapters_found'])}")
    else:
        print(f"\n✗ Validation failed: {result['error']}")

    # Example 2: Actually download (commented out by default)
    print("\n" + "="*70)
    print("EXAMPLE 2: Download chapters (uncomment to use)")
    print("="*70)
    print("To actually download, uncomment the code below in this script\n")

    # Uncomment to download:
    # result = service.download_manga_chapters(
    #     source_id="mangadex",
    #     manga_name="One Piece",
    #     chapter_numbers=[1, 2],  # Download first 2 chapters
    #     format="cbz",
    #     options={"quality": "high", "includeMetadata": True}
    # )
    #
    # if result["success"]:
    #     download_id = result["download"]["response"]["data"]["id"]
    #     print(f"\n✓ Download started! ID: {download_id}")
    #     print(f"\nCheck status:")
    #     print(f"  curl http://localhost:3000/api/v1/downloads/{download_id}")
    #     print(f"\nDownload file when ready:")
    #     print(f"  curl http://localhost:3000/api/v1/downloads/{download_id}/file -o manga.cbz")
    # else:
    #     print(f"\n✗ Download failed: {result['error']}")

    print("\n" + "="*70)
    print("Done! Check discover_and_download.py for interactive usage")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print("\nStart the server first:")
        print("  $ cd .. && npm run dev")
        print("\nThen run this script again.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
