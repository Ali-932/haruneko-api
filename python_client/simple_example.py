#!/usr/bin/env python3
"""
Simple example script for HaruNeko Download Service

This demonstrates the simplest way to validate and download manga chapters.
"""

from haruneko_download_service import HaruNekoDownloadService

# ============================================================================
# CONFIGURATION - Change these values for your manga
# ============================================================================

BASE_URL = "http://localhost:3000/api/v1"
SOURCE_ID = "mangahere"

# Manga details
MANGA_TITLE = "berserk"
POST = "4737"
SLUG = "/manga/berserk/"

# Chapters to download (update with actual chapter IDs from your API)
CHAPTER_IDS = [
    "/manga/berserk/c001/",
    "/manga/berserk/c002/",
    "/manga/berserk/c003/",
]

# Download settings
DOWNLOAD_FORMAT = "images"  # Options: images, cbz, pdf, epub
DOWNLOAD_OPTIONS = {
    "quality": "low",
    "includeMetadata": True,
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

def main():
    """Main function to validate and download manga chapters"""

    # Initialize the service
    print("Initializing HaruNeko Download Service...")
    service = HaruNekoDownloadService(
        base_url=BASE_URL,
        download_root="downloads"
    )

    # Validate and download
    print(f"\nProcessing: {MANGA_TITLE}")
    print(f"Source: {SOURCE_ID}")
    print(f"Chapters: {len(CHAPTER_IDS)}")
    print("-" * 60)

    result = service.validate_and_download(
        source_id=SOURCE_ID,
        manga_title=MANGA_TITLE,
        post=POST,
        slug=SLUG,
        chapter_ids=CHAPTER_IDS,
        format=DOWNLOAD_FORMAT,
        options=DOWNLOAD_OPTIONS,
        validate_only=False  # Set to True to only validate without downloading
    )

    # Print results
    print("\n" + "=" * 60)
    if result["success"]:
        print("✓ SUCCESS!")
        print(f"Manga: {result['validation']['manga_title']}")
        print(f"Chapters validated: {len(CHAPTER_IDS)}")
        print(f"Download status: {result['download']['status_code']}")
    else:
        print("✗ FAILED!")
        if result["validation"]:
            print(f"Error: {result['validation']['error']}")
            if result["validation"]["missing_chapters"]:
                print(f"Missing chapters: {result['validation']['missing_chapters']}")
        elif result["download"]:
            print(f"Error: {result['download']['error']}")
    print("=" * 60)

    return result


if __name__ == "__main__":
    main()
