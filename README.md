
# Prospect N-PORT API

A FastAPI service that retrieves the latest SEC N-PORT filing for a fund using its CIK, parses the filing XML, and returns normalized fund and holding data.

## API

`GET /nport/{cik}`

**Example:**
```text
https://nport-api.fastapicloud.dev/nport/0000036405
```

## Caching

Prospect uses DiskCache to reduce redundant requests to SEC EDGAR.

| Cache key | Data | TTL |
|---|---|---|
| `latest:{cik}` | Latest filing metadata | 12 hours |
| `filing:{accession}` | Raw filing XML | No expiration |

Filing metadata is refreshed periodically, while retrieved filing documents are cached by accession number and reused.

## Data Model

The API response consists of three primary components:

- **CIK:** Fund identifier
- **Filing:** Form type, filing date, and report date
- **Form data:** Fund information and normalized holdings

## Local Development

```bash
git clone https://github.com/j-soto35/nport-api.git
cd nport-api

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Local API: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

## Deployment

[https://nport-api.fastapicloud.dev](https://nport-api.fastapicloud.dev)
