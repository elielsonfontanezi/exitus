export TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{ "username": "admin", "password": "admin123" }' | \
  jq -r '.data.access_token')

echo $TOKEN
