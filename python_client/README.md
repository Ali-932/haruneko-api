# HaruNeko Python Client

Python client library for downloading manga via the HaruNeko API.

## Prerequisites

**⚠️ IMPORTANT: You MUST start the HaruNeko API server before using this client!**

### Starting the HaruNeko API Server

Navigate to the haruneko project root and run:

```bash
# Install dependencies (first time only)
npm install

# Build the project (first time only)
npm run build

# Start the server
npm run dev  # Development mode with auto-reload
# OR
npm start    # Production mode
```

The API will be available at `http://localhost:3000`

Verify it's running by visiting: http://localhost:3000/api-docs

## Features

- **Rate Limiting**: Automatic retry with exponential backoff for 429 errors
- **Search**: Find manga across multiple sources with pagination
- **Validation**: Check if chapters exist before downloading
- **Download**: Download chapters in multiple formats (images, cbz, pdf, epub)
- **Error Handling**: Comprehensive error handling and reporting

## Installation

```bash
cd python_client
pip install -r requirements.txt
```

## Quick Start

### 1. Understand How IDs Work

In HaruNeko, **manga IDs and chapter IDs vary by source**. Some sources use simple strings, others use JSON objects:

**Example for mangahere:**
- Manga ID: `"{\"post\":\"4737\",\"slug\":\"/manga/berserk/\"}"`  (JSON string)
- Chapter ID: `"/manga/berserk/c001/"` (simple string)

You'll discover these IDs by searching and exploring the API responses.

### 2. Discovering Available Manga

First, search for manga and inspect the results to find the correct IDs:

```python
from haruneko_download_service import HaruNekoDownloadService

service = HaruNekoDownloadService()

# Search for manga
results = service.search_manga("mangahere", "berserk", page=1, limit=10)

# Inspect the results
for manga in results[:3]:
    print(f"Title: {manga['title']}")
    print(f"ID: {manga['id']}")
    print()
```

### 3. Getting Chapters

Once you have a manga ID, fetch its chapters:

```python
# Use the manga ID from search results
manga_id = results[0]["id"]

chapters = service.fetch_chapters("mangahere", manga_id)

# Inspect chapters
for chapter in chapters[:5]:
    print(f"Title: {chapter['title']}")
    print(f"Chapter ID: {chapter['id']}")
    print()
```

### 4. Downloading Chapters

```python
# Download specific chapters
chapter_ids = [chapters[0]["id"], chapters[1]["id"]]

download_result = service.download_chapters(
    source_id="mangahere",
    manga_id_raw=manga_id,
    chapter_ids=chapter_ids,
    format="cbz",
    options={"quality": "high", "includeMetadata": True}
)

if download_result["success"]:
    print("Download initiated!")
    download_id = download_result["response"]["data"]["id"]
    print(f"Download ID: {download_id}")

    # Check status later
    # GET /api/v1/downloads/{download_id}
    # When complete: GET /api/v1/downloads/{download_id}/file
```

## Complete Workflow Example

```python
from haruneko_download_service import HaruNekoDownloadService

# Initialize
service = HaruNekoDownloadService(
    base_url="http://localhost:3000/api/v1"
)

# 1. Search for manga
print("[1] Searching for 'one piece'...")
results = service.search_manga("mangadex", "one piece", page=1, limit=5)
print(f"Found {len(results)} results")

if not results:
    print("No manga found!")
    exit(1)

# 2. Pick first result
manga = results[0]
manga_id = manga["id"]
print(f"\n[2] Selected: {manga['title']}")
print(f"Manga ID: {manga_id}")

# 3. Get chapters
print("\n[3] Fetching chapters...")
chapters = service.fetch_chapters("mangadex", manga_id)
print(f"Found {len(chapters)} chapters")

if not chapters:
    print("No chapters found!")
    exit(1)

# 4. Download first 3 chapters
chapter_ids = [ch["id"] for ch in chapters[:3]]
print(f"\n[4] Downloading {len(chapter_ids)} chapters...")

result = service.download_chapters(
    source_id="mangadex",
    manga_id_raw=manga_id,
    chapter_ids=chapter_ids,
    format="cbz",
    options={"quality": "high"}
)

if result["success"]:
    download_id = result["response"]["data"]["id"]
    print(f"✓ Download started! ID: {download_id}")
    print(f"Check status at: /api/v1/downloads/{download_id}")
else:
    print(f"✗ Download failed: {result['error']}")
```

## API Methods

### `search_manga(source_id, query, page=1, limit=100)`
Search for manga by title with pagination support.

**Parameters:**
- `source_id`: Source identifier (e.g., "mangadex", "mangahere")
- `query`: Search term
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 100)

**Returns:** List of manga dicts with `id`, `title`, `sourceId`, etc.

### `fetch_chapters(source_id, manga_id_raw)`
Fetch all chapters for a manga.

**Parameters:**
- `source_id`: Source identifier
- `manga_id_raw`: Manga ID (can be JSON string or simple string)

**Returns:** List of chapter dicts with `id`, `title`, `mangaId`, etc.

### `download_chapters(source_id, manga_id_raw, chapter_ids, format="cbz", options=None)`
Download multiple chapters.

**Parameters:**
- `source_id`: Source identifier
- `manga_id_raw`: Manga ID
- `chapter_ids`: List of chapter IDs to download
- `format`: Download format - `cbz`, `pdf`, `epub`, or `images` (default: cbz)
- `options`: Dict with `quality` ("low"|"medium"|"high") and `includeMetadata` (bool)

**Returns:** Dict with `success`, `error`, `response`, and `status_code`

### `get_manga_details(source_id, manga_id_raw)`
Get detailed information about a manga.

**Returns:** Manga details dict or None

## Response Structure

All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

## Rate Limiting

The service automatically handles rate limiting with exponential backoff:
- Initial delay: 3 seconds
- Max retries: 10
- Delay doubles with each retry (3s → 6s → 12s → 24s → ...)

## Supported Sources

The HaruNeko API supports 788+ manga sources. Common ones include:
- mangadex
- mangahere
- mangakakalot
- manganato
- And 780+ more!

To see all available sources:
```bash
curl http://localhost:3000/api/v1/sources?limit=1000
```

## Checking Download Status

After initiating a download, you'll receive a download ID. Use it to check status:

```python
import requests

download_id = "your-download-id-here"
response = requests.get(f"http://localhost:3000/api/v1/downloads/{download_id}")
status = response.json()

print(f"Status: {status['data']['status']}")
print(f"Progress: {status['data']['progress']}%")

# When completed, download the file:
if status['data']['status'] == 'completed':
    file_url = f"http://localhost:3000{status['data']['fileUrl']}"
    print(f"Download file at: {file_url}")
```

## Testing

Run the test script:

```bash
# Make sure API server is running first!
python test_client.py
```

Or run a simple discovery script:

```bash
python simple_example.py
```

## Troubleshooting

### Connection Refused Error
```
ConnectionError: [Errno 111] Connection refused
```

**Solution:** Start the HaruNeko API server first!
```bash
cd .. && npm run dev
```

### Invalid Manga/Chapter IDs

**Solution:** Always discover IDs through the API by searching first. Don't hardcode IDs - they vary by source.

### Rate Limiting (429 Errors)

**Solution:** The client handles this automatically with retries. If you still see errors, reduce concurrent requests.

## Requirements

- Python 3.7+
- requests >= 2.31.0
- HaruNeko API server running (default: http://localhost:3000)

## License

Same as HaruNeko project (Unlicense)
