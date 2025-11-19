#!/usr/bin/env python3
"""
Test Script - Simplified API Testing

This script tests the simplified download_manga_chapters() API.

Prerequisites:
    1. Start HaruNeko API: cd .. && npm run dev
    2. Run this script: python test_simple.py
"""

from haruneko_download_service import HaruNekoDownloadService


def test_validate_only():
    """Test validation without downloading"""
    print("\n" + "="*70)
    print("TEST 1: Validate manga and chapters")
    print("="*70)

    service = HaruNekoDownloadService()

    result = service.download_manga_chapters(
        source_id="mangadex",
        manga_name="One Piece",
        chapter_numbers=[1, 2, 3],
        validate_only=True
    )

    print("\nResult:")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Manga: {result['manga']['title']}")
        print(f"  Chapters matched: {len(result['chapters_found'])}")
    else:
        print(f"  Error: {result['error']}")

    return result


def test_missing_chapters():
    """Test with chapters that don't exist"""
    print("\n" + "="*70)
    print("TEST 2: Request non-existent chapters")
    print("="*70)

    service = HaruNekoDownloadService()

    result = service.download_manga_chapters(
        source_id="mangadex",
        manga_name="One Piece",
        chapter_numbers=[99999, 99998],  # These probably don't exist
        validate_only=True
    )

    print("\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Error: {result.get('error', 'None')}")
    print(f"  Missing: {result['chapters_missing']}")

    return result


def test_download():
    """Test actual download (if uncommented)"""
    print("\n" + "="*70)
    print("TEST 3: Download chapters")
    print("="*70)
    print("⚠️  This test is commented out to avoid actual downloads")
    print("Uncomment the code below to test downloading\n")

    # Uncomment to test actual download:
    # service = HaruNekoDownloadService()
    #
    # result = service.download_manga_chapters(
    #     source_id="mangadex",
    #     manga_name="One Piece",
    #     chapter_numbers=[1],
    #     format="cbz"
    # )
    #
    # if result['success']:
    #     download_id = result['download']['response']['data']['id']
    #     print(f"\n✓ Download initiated! ID: {download_id}")
    # else:
    #     print(f"\n✗ Failed: {result['error']}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         HaruNeko API - Simplified API Test Suite                ║
╚══════════════════════════════════════════════════════════════════╝

This tests the new simplified API that only needs:
  - source_id (e.g., "mangadex")
  - manga_name (e.g., "One Piece")
  - chapter_numbers (e.g., [1, 2, 3])
""")

    try:
        # Test 1: Validate manga and chapters
        test_validate_only()

        # Test 2: Non-existent chapters
        test_missing_chapters()

        # Test 3: Download (commented out)
        test_download()

        print("\n" + "="*70)
        print("Tests complete!")
        print("="*70)

    except ConnectionError:
        print("\n❌ ERROR: Cannot connect to API!")
        print("\nMake sure the server is running:")
        print("  $ cd .. && npm run dev")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
