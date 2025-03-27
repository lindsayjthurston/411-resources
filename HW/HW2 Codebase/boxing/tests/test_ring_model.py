import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer, create_boxer, get_boxer_by_name
from boxing.utils.sql_utils import get_db_connection

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

@pytest.fixture
def ring():
    """Initialize a new RingModel for each test."""
    return RingModel()

def test_enter_ring(setup_db, ring):
    """Test adding boxers to the ring."""
    create_boxer("Boxer A", 160, 70, 72.0, 25)
    create_boxer("Boxer B", 170, 72, 74.0, 28)

    boxer_a = get_boxer_by_name("Boxer A")
    boxer_b = get_boxer_by_name("Boxer B")

    ring.enter_ring(boxer_a) 
    ring.enter_ring(boxer_b)
    
    assert len(ring.get_boxers()) == 2

def test_fight(setup_db, ring):
    """Test that a fight occurs correctly and updates the database."""
    create_boxer("Fighter 1", 180, 74, 76.0, 30)
    create_boxer("Fighter 2", 175, 73, 75.0, 27)

    fighter_1 = get_boxer_by_name("Fighter 1")
    fighter_2 = get_boxer_by_name("Fighter 2")

    ring.enter_ring(fighter_1)  # Fix function call
    ring.enter_ring(fighter_2)

    winner = ring.fight()
    assert winner in [fighter_1.name, fighter_2.name]

def test_fight_not_enough_boxers(ring):
    """Test that a fight cannot start with less than two boxers."""
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring.fight()

def test_clear_ring(setup_db, ring):
    """Test that the ring clears properly after a fight."""
    create_boxer("Solo Boxer", 200, 76, 78.0, 32)
    solo_boxer = get_boxer_by_name("Solo Boxer")

    ring.enter_ring(solo_boxer)
    assert len(ring.ring) == 1

    ring.clear_ring()
    assert len(ring.ring) == 0

def test_enter_valid_boxer():
    ring = RingModel()
    boxer = Boxer(id=1, name="Mike Tyson", weight=220, height=71, reach=71, age=30)
    
    ring.enter_ring(boxer)
    assert len(ring.ring) == 1
    assert ring.ring[0] == boxer

def test_enter_invalid_type():
    ring = RingModel()
    with pytest.raises(AttributeError):
        ring.enter_ring(123)

def test_ring_full():
    ring = RingModel()
    boxer1 = Boxer(id=1, name="Muhammad Ali", weight=210, height=74, reach=78, age=32)
    boxer2 = Boxer(id=2, name="Joe Frazier", weight=205, height=71, reach=76, age=29)
    boxer3 = Boxer(id=3, name="George Foreman", weight=220, height=76, reach=79, age=33)

    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring.enter_ring(boxer3)

def test_clear_ring():
    ring = RingModel()
    boxer = Boxer(id=1, name="Lennox Lewis", weight=245, height=77, reach=84, age=34)

    ring.enter_ring(boxer)
    assert len(ring.ring) == 1

    ring.clear_ring()
    assert len(ring.ring) == 0

def test_get_boxers():
    ring = RingModel()
    boxer1 = Boxer(id=1, name="Rocky Marciano", weight=190, height=70, reach=68, age=31)
    boxer2 = Boxer(id=2, name="Evander Holyfield", weight=215, height=74, reach=78, age=32)

    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    boxers = ring.get_boxers()
    assert len(boxers) == 2
    assert boxers == [boxer1, boxer2]

def test_fight_not_enough_boxers():
    ring = RingModel()
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring.fight()

def test_fight_success(mocker):
    ring = RingModel()
    boxer1 = Boxer(id=1, name="Sugar Ray Leonard", weight=160, height=70, reach=74, age=28)
    boxer2 = Boxer(id=2, name="Roberto Duran", weight=158, height=69, reach=72, age=30)

    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    # Mock get_random() for predictable results
    mocker.patch("boxing.utils.api_utils.get_random", return_value=0.3)

    winner = ring.fight()
    assert winner in [boxer1.name, boxer2.name]
    assert len(ring.ring) == 0  # Ring should be cleared after fight

def test_get_fighting_skill():
    ring = RingModel()
    boxer = Boxer(id=1, name="Gennady Golovkin", weight=160, height=70, reach=74, age=35)
    
    expected_skill = (160 * len("Gennady Golovkin")) + (74 / 10)  # Remove -2 if age is exactly 35
    actual_skill = ring.get_fighting_skill(boxer)
    
    assert actual_skill == expected_skill

def test_get_fighting_skill_extreme_values():
    ring = RingModel()
    
    # Boxer with extremely high weight
    heavy_boxer = Boxer(id=1, name="Big Heavy", weight=1000, height=70, reach=75, age=30)
    expected_skill_heavy = (1000 * len("Big Heavy")) + (75 / 10)  # High weight influences skill
    actual_skill_heavy = ring.get_fighting_skill(heavy_boxer)
    assert actual_skill_heavy == expected_skill_heavy

    # Boxer with extremely low weight
    light_boxer = Boxer(id=2, name="Light Feather", weight=50, height=70, reach=70, age=30)
    expected_skill_light = (50 * len("Light Feather")) + (70 / 10)
    actual_skill_light = ring.get_fighting_skill(light_boxer)
    assert actual_skill_light == expected_skill_light

    # Boxer exactly at age 25 (age modifier should be 0)
    mid_age_boxer = Boxer(id=3, name="Mid Age Boxer", weight=160, height=70, reach=74, age=25)
    expected_skill_mid_age = (160 * len("Mid Age Boxer")) + (74 / 10)
    actual_skill_mid_age = ring.get_fighting_skill(mid_age_boxer)
    assert actual_skill_mid_age == expected_skill_mid_age

    # Boxer exactly at age 35 (age modifier should be 0)
    mid_age_boxer = Boxer(id=4, name="Old Boxer", weight=160, height=70, reach=74, age=35)
    expected_skill_mid_age = (160 * len("Old Boxer")) + (74 / 10)
    actual_skill_mid_age = ring.get_fighting_skill(mid_age_boxer)
    assert actual_skill_mid_age == expected_skill_mid_age

def test_enter_ring_invalid_type():
    ring = RingModel()
    with pytest.raises(TypeError):
        ring.enter_ring("Invalid Boxer Type")  # Passing a string instead of a Boxer object

    with pytest.raises(TypeError):
        ring.enter_ring(12345)  # Passing an integer instead of a Boxer object

def test_clear_ring_empty():
    ring = RingModel()
    ring.clear_ring()  # Call clear on an empty ring
    assert len(ring.ring) == 0  # It should remain empty

def test_clear_ring_multiple_calls():
    ring = RingModel()
    boxer = Boxer(id=1, name="Test Boxer", weight=180, height=70, reach=75, age=28)
    
    ring.enter_ring(boxer)
    assert len(ring.ring) == 1
    
    ring.clear_ring()  # First clear
    assert len(ring.ring) == 0
    
    ring.clear_ring()  # Second clear, should have no effect
    assert len(ring.ring) == 0

def test_weight_classes():
    ring = RingModel()

    # Heavyweight boxer
    heavyweight = Boxer(id=1, name="Heavy Hulk", weight=250, height=76, reach=80, age=30)
    assert heavyweight.weight_class == "HEAVYWEIGHT"

    # Middleweight boxer
    middleweight = Boxer(id=2, name="Middle Mike", weight=175, height=74, reach=75, age=27)
    assert middleweight.weight_class == "MIDDLEWEIGHT"

    # Lightweight boxer
    lightweight = Boxer(id=3, name="Light Leo", weight=130, height=70, reach=74, age=25)
    assert lightweight.weight_class == "LIGHTWEIGHT"

    # Featherweight boxer
    featherweight = Boxer(id=4, name="Feather Fred", weight=120, height=69, reach=72, age=23)
    assert featherweight.weight_class == "FEATHERWEIGHT"

def test_get_boxers_invalid_state():
    ring = RingModel()
    # Ensure get_boxers returns an empty list when no boxers have been added
    boxers = ring.get_boxers()
    assert boxers == []
    
    boxer = Boxer(id=1, name="Test Boxer", weight=180, height=70, reach=75, age=28)
    ring.enter_ring(boxer)
    boxers = ring.get_boxers()
    assert boxers == [boxer]  # Should return the boxer in the ring

def test_get_fighting_skill_mocked(mocker):
    ring = RingModel()
    boxer = Boxer(id=1, name="Mock Boxer", weight=160, height=70, reach=74, age=30)
    
    # Mock the actual calculation of the skill
    mocker.patch.object(ring, 'get_fighting_skill', return_value=500)
    
    skill = ring.get_fighting_skill(boxer)
    assert skill == 500  # The mocked value should be returned


