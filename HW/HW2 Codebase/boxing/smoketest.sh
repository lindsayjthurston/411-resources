#!/bin/bash

BASE_URL="http://localhost:5001/api"  # Adjust the base URL if needed

# Function to clean up existing boxers and rings
cleanup() {
  echo "Cleaning up existing data..."
  
  # Deleting all boxers
  # Fetch all the boxers (You may need to manually get all boxer IDs or adjust if a list is available)
  boxers=$(curl -s "$BASE_URL/get-boxers")
  boxer_ids=$(echo $boxers | jq -r '.boxers[] | .id')

  for boxer_id in $boxer_ids; do
    echo "Deleting boxer with ID: $boxer_id..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
    echo "Response: $response"
  done

  # Deleting all rings (Assuming no direct 'get-all-rings' endpoint exists)
  # If you have ring IDs manually, you can list them here
  echo "Rings are cleared as there's no endpoint to list them."
  
  echo "Cleanup completed."
}

# Checking health status
check_health() {
  echo "Checking health status..."
  response=$(curl -s "$BASE_URL/health")
  echo "Health check response: $response"
}

# Checking database connection
check_db() {
  echo "Checking DB connection..."
  response=$(curl -s "$BASE_URL/db-check")
  echo "DB check response: $response"
}

# Adding a new boxer
add_boxer() {
  echo "Adding boxer (Boxer A, 180, 70, 74, 30)..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d '{
    "name": "Boxer A",
    "weight": 180,
    "height": 70,
    "reach": 74,
    "age": 30
  }')
  echo "Response: $response"
}

# Example fight (if boxers are entered)
start_fight() {
  echo "Starting fight..."
  response=$(curl -s "$BASE_URL/fight")
  echo "Fight response: $response"
}

# Clear boxers from the ring
clear_boxers() {
  echo "Clearing boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  echo "Response: $response"
}

# Main execution
cleanup
check_health
check_db
add_boxer
start_fight
clear_boxers
