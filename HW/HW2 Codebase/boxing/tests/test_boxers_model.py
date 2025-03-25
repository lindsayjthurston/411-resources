import os
import pytest
import sqlite3
from boxing.models.boxers_model import create_boxer
from boxing.models.boxers_model import get_weight_class

from boxing.utils.sql_utils import get_db_connection

DB_PATH = os.getenv("DB_PATH", "/app/sql/boxing.db")

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
                    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 40)
                )
            """)
            conn.commit()
            yield conn  # Yield connection so tests can use it
    finally:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS boxers")
            conn.commit()


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

def test_get_weight_class_heavyweight():
    assert get_weight_class(210) == "HEAVYWEIGHT"

def test_get_weight_class_middleweight():
    assert get_weight_class(170) == "MIDDLEWEIGHT"

def test_get_weight_class_invalid_weight():
    with pytest.raises(ValueError):
        get_weight_class(120)
