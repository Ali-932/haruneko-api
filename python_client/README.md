# HaruNeko Python Client

Python client library for downloading manga via the HaruNeko API.

## Features

- **Rate Limiting**: Automatic retry with exponential backoff for 429 errors
- **Search**: Find manga across multiple sources with pagination
- **Validation**: Check if chapters exist before downloading
- **Download**: Download chapters in multiple formats (images, cbz, pdf, epub)
- **Error Handling**: Comprehensive error handling and reporting

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from haruneko_download_service import HaruNekoDownloadService

# Initialize service
service = HaruNekoDownloadService(
    base_url="http://localhost:3000/api/v1",
    download_root="downloads"
)

# Validate and download chapters
result = service.validate_and_download(
    source_id="mangahere",
    manga_title="berserk",
    post="4737",
    slug="/manga/berserk/",
    chapter_ids=[
        "/manga/berserk/c001/",
        "/manga/berserk/c002/",
    ],
    format="images",
    validate_only=False  # Set to True for dry-run
)

print(result)
```

### Manual Workflow

```python
# Step 1: Search for manga
results = service.search_manga("mangahere", "berserk", page=1, limit=100)

# Step 2: Resolve exact manga by post + slug
manga = service.resolve_manga_id("mangahere", "berserk", "4737", "/manga/berserk/")

# Step 3: Fetch chapters
chapters = service.fetch_chapters("mangahere", manga["id"])

# Step 4: Validate chapters
validation = service.validate_manga_has_chapters(
    source_id="mangahere",
    manga_title="berserk",
    post="4737",
    slug="/manga/berserk/",
    chapter_ids=[chapters[0]["id"], chapters[1]["id"]]
)

# Step 5: Download if validation passed
if validation["success"]:
    download_result = service.download_chapters(
        source_id="mangahere",
        manga_id_raw=manga["id"],
        chapter_ids=[chapters[0]["id"], chapters[1]["id"]],
        format="images"
    )
```

## API Methods

### `search_manga(source_id, query, page=1, limit=100)`
Search for manga by title with pagination support.

**Returns:** List of manga search results

### `resolve_manga_id(source_id, query, post, slug, max_pages=5)`
Find manga by exact match on post ID and slug.

**Returns:** Matched manga dict or None

### `fetch_chapters(source_id, manga_id_raw)`
Fetch all chapters for a manga.

**Returns:** List of chapter dicts

### `validate_manga_has_chapters(source_id, manga_title, post, slug, chapter_ids)`
Validate that all required chapters exist.

**Returns:** Dict with validation results:
```python
{
    "success": bool,
    "manga_id": str,
    "manga_title": str,
    "missing_chapters": List[str],
    "error": Optional[str]
}
```

### `download_chapters(source_id, manga_id_raw, chapter_ids, format="images", options=None)`
Download multiple chapters.

**Supported formats:**
- `images` - Individual image files
- `cbz` - Comic book archive
- `pdf` - PDF document
- `epub` - EPUB ebook

**Returns:** Dict with download results:
```python
{
    "success": bool,
    "error": Optional[str],
    "response": Dict,
    "status_code": int
}
```

### `validate_and_download(source_id, manga_title, post, slug, chapter_ids, format="images", validate_only=False)`
All-in-one method: validate chapters exist, then download them.

**Returns:** Dict with both validation and download results

## Rate Limiting

The service automatically handles rate limiting with exponential backoff:
- Initial delay: 3 seconds
- Max retries: 10
- Delay doubles with each retry (3s → 6s → 12s → 24s → ...)

## Error Handling

The service handles various error scenarios:
- 429 Too Many Requests (automatic retry)
- Manga not found
- Missing chapters
- Network errors
- Invalid responses

## Testing

Run the test suite:

```bash
python test_client.py
```

The test suite includes:
1. Basic validate + download example
2. Manual step-by-step workflow
3. Error handling tests

## Example Response

### Successful Validation
```json
{
  "success": true,
  "validation": {
    "success": true,
    "manga_id": "{\"post\":\"4737\",\"slug\":\"/manga/berserk/\"}",
    "manga_title": "Berserk",
    "missing_chapters": [],
    "error": null
  },
  "download": {
    "success": true,
    "error": null,
    "response": { ... },
    "status_code": 200
  }
}
```

### Failed Validation
```json
{
  "success": false,
  "validation": {
    "success": false,
    "manga_id": "{\"post\":\"4737\",\"slug\":\"/manga/berserk/\"}",
    "manga_title": "Berserk",
    "missing_chapters": ["/manga/berserk/c999/"],
    "error": "Missing chapters: ['/manga/berserk/c999/']"
  },
  "download": null
}
```

## Requirements

- Python 3.7+
- requests >= 2.31.0
- HaruNeko API server running (default: http://localhost:3000)

## License

Same as HaruNeko project
