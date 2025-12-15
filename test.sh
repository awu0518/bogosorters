source .venv/bin/activate

mongod --config /opt/homebrew/etc/mongod.conf 

lsof -iTCP:27017 -sTCP:LISTEN || ps aux | grep mongod | grep -v grep

./local

# set CLOUD_MONGO=0 for local testing

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

curl -X POST http://127.0.0.1:8000/cities \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{"name": "New York3", "state_code": "NT"}'
#delte
curl -sS -X DELETE "http://127.0.0.1:8000/cities/New%20York3?state_code=NT"

  # Create France
curl -X POST http://127.0.0.1:8000/countries \
  -H "Content-Type: application/json" \
  -d '{"name": "France", "iso_code": "FR"}'

# Create Japan
curl -X POST http://127.0.0.1:8000/countries \
  -H "Content-Type: application/json" \
  -d '{"name": "Japan", "iso_code": "JP"}'


# basic discovery / simple endpoints
curl -sS http://127.0.0.1:8000/endpoints
curl -sS http://127.0.0.1:8000/hello
curl -sS http://127.0.0.1:8000/timestamp

# random number with bounds
curl -sS "http://127.0.0.1:8000/random?min=10&max=20"

# dice endpoints: GET default and POST custom
curl -sS http://127.0.0.1:8000/dice
curl -sS -X POST http://127.0.0.1:8000/dice \
  -H "Content-Type: application/json" \
  -d '{"num_dice":3,"sides":8}'

# health (includes DB stats)
curl -sS http://127.0.0.1:8000/health

# search examples
curl -sS "http://127.0.0.1:8000/cities/search?name=New"
curl -sS "http://127.0.0.1:8000/cities/search?state_code=NY"
curl -sS "http://127.0.0.1:8000/countries/search?name=Japan"
curl -sS "http://127.0.0.1:8000/countries/search?iso_code=JP"
curl -sS "http://127.0.0.1:8000/states/search?capital=Albany"

# create / update / delete flows for quick smoke tests
curl -sS -X POST http://127.0.0.1:8000/states \
  -H "Content-Type: application/json" \
  -d '{"name": "TestState", "state_code": "TS", "capital": "Testville"}'

curl -sS -X POST http://127.0.0.1:8000/cities \
  -H "Content-Type: application/json" \
  -d '{"name": "TestCity", "state_code": "TS"}'

# delete city by name (requires state_code)
curl -sS -X DELETE "http://127.0.0.1:8000/cities/TestCity?state_code=TS"

# country get/put/delete by id (id is name in this API)
curl -sS http://127.0.0.1:8000/countries/France
curl -sS -X PUT http://127.0.0.1:8000/countries/France \
  -H "Content-Type: application/json" \
  -d '{"name": "France", "iso_code": "FR"}'
curl -sS -X DELETE http://127.0.0.1:8000/countries/France

# state get/put/delete by id
curl -sS http://127.0.0.1:8000/states/TestState
curl -sS -X PUT http://127.0.0.1:8000/states/TestState \
  -H "Content-Type: application/json" \
  -d '{"capital": "NewTestville"}'
curl -sS -X DELETE http://127.0.0.1:8000/states/TestState

# bulk operations (countries)
curl -sS -X POST http://127.0.0.1:8000/countries/bulk \
  -H "Content-Type: application/json" \
  -d '[{"name":"TestLand1","iso_code":"TL1"},{"name":"TestLand2","iso_code":"TL2"}]'

curl -sS -X DELETE http://127.0.0.1:8000/countries/bulk \
  -H "Content-Type: application/json" \
  -d '["TestLand1","TestLand2"]'

# bulk create cities and delete
curl -sS -X POST http://127.0.0.1:8000/cities/bulk \
  -H "Content-Type: application/json" \
  -d '[{"name":"BulkCity1","state_code":"NY"},{"name":"BulkCity2","state_code":"NY"}]'

curl -sS -X DELETE http://127.0.0.1:8000/cities/bulk \
  -H "Content-Type: application/json" \
  -d '[{"name":"BulkCity1","state_code":"NY"},{"name":"BulkCity2","state_code":"NY"}]'

# end of added tests