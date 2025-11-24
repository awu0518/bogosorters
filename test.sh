curl http://127.0.0.1:8000/cities

curl http://127.0.0.1:8000/countries

curl -X POST http://127.0.0.1:8000/cities \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{"name": "New York", "state_code": "NY"}'

curl -X POST http://127.0.0.1:8000/cities \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{"name": "New York2", "state_code": "NY2"}'

  # Create France
curl -X POST http://127.0.0.1:8000/countries \
  -H "Content-Type: application/json" \
  -d '{"name": "France", "iso_code": "FR"}'

# Create Japan
curl -X POST http://127.0.0.1:8000/countries \
  -H "Content-Type: application/json" \
  -d '{"name": "Japan", "iso_code": "JP"}'