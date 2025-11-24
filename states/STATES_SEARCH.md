# States Search API

## Endpoint

```
GET /states/search
```

## Description

Search states by name substring, state code, and/or capital city name. All parameters are case-insensitive.

## Query Parameters

- `name` (string, optional): Substring to search in state names
- `state_code` (string, optional): Exact state code to filter by (2 letters)
- `capital` (string, optional): Substring to search in capital city names

At least one parameter must be provided.

## Examples

### Search by name
```bash
GET /states/search?name=new
```

Returns all states with "new" in their name (e.g., New York, New Jersey, New Mexico).

### Search by state code
```bash
GET /states/search?state_code=NY
```

Returns the state with code NY (New York).

### Search by capital
```bash
GET /states/search?capital=spring
```

Returns states with "spring" in their capital name (e.g., Springfield).

### Combined search
```bash
GET /states/search?name=new&capital=city
```

Returns states with "new" in the name and "city" in the capital.

## Response Format

```json
{
  "states": {
    "New York": {
      "name": "New York",
      "state_code": "NY",
      "capital": "Albany"
    },
    "New Jersey": {
      "name": "New Jersey",
      "state_code": "NJ",
      "capital": "Trenton"
    }
  },
  "count": 2
}
```

## Error Response

```json
{
  "error": "Provide at least one parameter: name, state_code, or capital"
}
```

Status code: 400

