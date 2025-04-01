#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

check_health_status() {
  echo "Checking health status"
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "It is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking DB connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "DB connection is healthy."
  else
    echo "DB connection check failed."
    exit 1
  fi
}

##########################################################
#
# Boxer Management
#
##########################################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer: $name, $weight lbs, $height in, $reach in reach, age $age..."
  response=$(curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  
  if echo "$response" | grep -q '"status": "success"'; then 
    echo "Boxer created"
  else 
    echo "Unable to create boxer"
    exit 1
  fi
}

delete_boxer() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer with ID $boxer_id deleted."
  else
    echo "Unable to delete boxer with ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer received by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Unable to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1

  echo "Getting boxer by name ($boxer_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$(echo $boxer_name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer received by name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Unable to get boxer by name ($boxer_name)."
    exit 1
  fi
}

get_leaderboard() {
  sort=$1
  echo "Getting leaderboard sorted by $sort..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard received successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by $sort):"
      echo "$response" | jq .
    fi
  else
    echo $response
    echo "Unable to get leaderboard."
    exit 1
  fi
}

##########################################################
#
# Ring Management
#
##########################################################

create_ring() {
  echo "Creating a new ring..."
  response=$(curl -s -X POST "$BASE_URL/create-ring")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring created successfully."
  else
    echo "Unable to create ring."
    exit 1
  fi
}

enter_ring() {
  boxer_id=$1
  echo "Boxer with ID $boxer_id is entering the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer with ID $boxer_id has entered the ring."
  else
    echo "Unable to add boxer with ID $boxer_id to the ring."
    exit 1
  fi
}

start_fight() {
  echo "Starting a fight in the ring..."
  response=$(curl -s -X POST "$BASE_URL/start-fight")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight started successfully."
  else
    echo "Unable to start fight."
    exit 1
  fi
}

clear_ring() {
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-ring")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Unable to clear the ring."
    exit 1
  fi
}

# Health checks
check_health_status
check_db

# Create test boxers
create_boxer "Boxer A" 180 70 74 30
create_boxer "Boxer B" 170 68 73 28

# Get test boxers by name and ID
get_boxer_by_name "Boxer A"
get_boxer_by_name "Boxer B"

# Get leaderboard sorted by wins
get_leaderboard "wins"

# Create a new ring and enter test boxers
create_ring
enter_ring 1
enter_ring 2

# Start a fight
start_fight

# Clear the ring after the fight
clear_ring

# Delete a boxer
delete_boxer 1  # Replace with the actual ID of a boxer

echo "All smoketests completed successfully!"
