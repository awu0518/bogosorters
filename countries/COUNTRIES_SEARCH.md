# Countries Search API

## Endpoint

```
GET /countries/search
```

## Description

Search countries by name substring and/or ISO code. Both parameters are case-insensitive.

## Query Parameters

- `name` (string, optional): Substring to search in country names
- `iso_code` (string, optional): Exact ISO code to filter by

At least one parameter must be provided.

## Examples

### Search by name
```bash
GET /countries/search?name=united
```

Returns all countries with "united" in their name (e.g., United States, United Kingdom).

### Search by ISO code
```bash
GET /countries/search?iso_code=US
```

Returns the country with ISO code "US".

### Combined search
```bash
GET /countries/search?name=kingdom&iso_code=GB
```

Returns countries with "kingdom" in their name and ISO code "GB".

## Response Format

```json
{
  "countries": {
    "United States": {
      "name": "United States",
      "iso_code": "US"
    },
    "United Kingdom": {
      "name": "United Kingdom",
      "iso_code": "GB"
    }
  },
  "count": 2
}
```

## Error Response

```json
{
  "error": "Provide at least one parameter: name or iso_code"
}
```

Status code: 400

