import os
import pytest
import sqlite3
from unittest.mock import patch
from boxing.models.boxers_model import create_boxer, delete_boxer, get_boxer_by_name, get_boxer_by_id, get_weight_class, update_boxer_stats, get_leaderboard
from boxing.utils.sql_utils import get_db_connection
from boxing.models.boxers_model import Boxer

DB_PATH = os.getenv("DB_PATH", "/app/sql/boxing.db")

# Fixture to set up and tear down the database for each test
@pytest.fixture(scope="module")
def setup_db():
    conn = None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS boxers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    weight INTEGER NOT NULL CHECK (weight > 0),
                    height INTEGER NOT NULL CHECK (height > 0),
                    reach REAL CHECK (reach > 0),
                    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 40),
                    fights INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            yield conn  # Yield connection so tests can use it
    finally:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS boxers")
            conn.commit()

# Create boxer tests
def test_create_boxer_valid(setup_db):
    create_boxer("Mike Tyson", 220, 72, 80.0, 30)
    cursor = setup_db.cursor()
    cursor.execute("SELECT name, weight FROM boxers WHERE name = 'Mike Tyson'")
    boxer = cursor.fetchone()
    assert boxer is not None
    assert boxer[0] == "Mike Tyson"
    assert boxer[1] == 220

def test_create_boxer_invalid_weight(setup_db):
    with pytest.raises(ValueError, match="Invalid weight: 100. Must be at least 125."):
        create_boxer("Invalid Boxer", 100, 72, 80.0, 30)

def test_create_boxer_invalid_height(setup_db):
    with pytest.raises(ValueError, match="Invalid height: -5. Must be greater than 0."):
        create_boxer("Invalid Boxer", 150, -5, 80.0, 30)

def test_create_boxer_invalid_reach(setup_db):
    with pytest.raises(ValueError, match="Invalid reach: -1. Must be greater than 0."):
        create_boxer("Invalid Boxer", 150, 72, -1, 30)

def test_create_boxer_invalid_age(setup_db):
    with pytest.raises(ValueError, match="Invalid age: 50. Must be between 18 and 40."):
        create_boxer("Old Boxer", 150, 72, 80.0, 50)

def test_create_boxer_duplicate_name(setup_db):
    create_boxer("Muhammad Ali", 220, 72, 80.0, 30)
    with pytest.raises(ValueError, match="Boxer with name 'Muhammad Ali' already exists"):
        create_boxer("Muhammad Ali", 230, 73, 85.0, 32)

# Get boxer by ID and name
def test_get_boxer_by_name(setup_db):
    create_boxer("Floyd Mayweather", 150, 68, 72.0, 40)
    boxer = get_boxer_by_name("Floyd Mayweather")
    assert boxer.name == "Floyd Mayweather"
    assert boxer.weight == 150

def test_get_boxer_by_name_not_found(setup_db):
    with pytest.raises(ValueError, match="Boxer 'Non Existent' not found."):
        get_boxer_by_name("Non Existent")

def test_get_boxer_by_id(setup_db):
    create_boxer("Sugar Ray Leonard", 160, 70, 74.0, 30)
    boxer = get_boxer_by_id(1)
    assert boxer.name == "Sugar Ray Leonard"
    assert boxer.weight == 160

def test_get_boxer_by_id_not_found(setup_db):
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        get_boxer_by_id(999)

# Update boxer stats
def test_update_boxer_stats_win(setup_db):
    create_boxer("Manny Pacquiao", 140, 67, 70.0, 35)
    update_boxer_stats(1, 'win')
    cursor = setup_db.cursor()
    cursor.execute("SELECT fights, wins FROM boxers WHERE id = 1")
    result = cursor.fetchone()
    assert result == (1, 1)

def test_update_boxer_stats_loss(setup_db):
    create_boxer("Oscar De La Hoya", 160, 68, 72.0, 40)
    update_boxer_stats(2, 'loss')
    cursor = setup_db.cursor()
    cursor.execute("SELECT fights, wins FROM boxers WHERE id = 2")
    result = cursor.fetchone()
    assert result == (1, 0)

def test_update_boxer_stats_invalid_result(setup_db):
    create_boxer("Canelo Alvarez", 175, 70, 74.0, 28)
    with pytest.raises(ValueError, match="Invalid result: 'draw' for boxer ID 3"):
        update_boxer_stats(3, 'draw')

# Leaderboard Tests
def test_get_leaderboard_wins(setup_db):
    create_boxer("Gennady Golovkin", 160, 70, 74.0, 37)
    create_boxer("Terence Crawford", 147, 69, 75.0, 33)
    update_boxer_stats(1, 'win')
    update_boxer_stats(2, 'win')
    leaderboard = get_leaderboard("wins")
    assert leaderboard[0]['name'] == "Gennady Golovkin"
    assert leaderboard[1]['name'] == "Terence Crawford"

def test_get_leaderboard_win_pct(setup_db):
    create_boxer("Vasyl Lomachenko", 135, 67, 69.0, 31)
    update_boxer_stats(1, 'win')
    leaderboard = get_leaderboard("win_pct")
    assert leaderboard[0]['name'] == "Vasyl Lomachenko"
    assert leaderboard[0]['win_pct'] == 100.0

def test_get_leaderboard_invalid_sort_by(setup_db):
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_field"):
        get_leaderboard("invalid_field")

# Get weight class
def test_get_weight_class_heavyweight():
    assert get_weight_class(210) == "HEAVYWEIGHT"

def test_get_weight_class_middleweight():
    assert get_weight_class(170) == "MIDDLEWEIGHT"

def test_get_weight_class_invalid_weight():
    with pytest.raises(ValueError):
        get_weight_class(120)

# Delete boxer tests
def test_delete_boxer_valid(setup_db):
    create_boxer("George Foreman", 220, 76, 79.0, 35)
    delete_boxer(1)
    cursor = setup_db.cursor()
    cursor.execute("SELECT id FROM boxers WHERE id = 1")
    result = cursor.fetchone()
    assert result is None

def test_delete_boxer_not_found(setup_db):
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        delete_boxer(999)

# Mocking tests 
def test_get_weight_class_mocked():
    with patch("boxing.models.boxers_model.get_weight_class", return_value="MIDDLEWEIGHT") as mock:
        result = get_weight_class(170)
        assert result == "MIDDLEWEIGHT"
        mock.assert_called_once_with(170)

