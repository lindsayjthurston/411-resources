from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)



@dataclass
class Boxer:
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer and adds them to the database.

    Args:
        name (str): The name of the boxer (must be unique).
        weight (int): The boxer's weight in pounds (must be at least 125).
        height (int): The boxer's height in inches (must be greater than 0).
        reach (float): The boxer's reach in inches (must be greater than 0).
        age (int): The boxer's age (must be between 18 and 40).

    Raises:
        ValueError: If any input is invalid or if the boxer's name already exists.
        sqlite3.Error: For unexpected database errors.
    """

    logger.info(f"Received request to create boxer: {name}")

    if weight < 125:
        logger.error(f"Invalid weight for boxer '{name}': {weight}")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Invalid height for boxer '{name}': {height}")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Invalid reach for boxer '{name}': {reach}")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Invalid age for boxer '{name}': {age}")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Successfully created boxer: {name}")

    except sqlite3.IntegrityError:
        logger.error(f"Integrity error when creating boxer '{name}' (likely duplicate)")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error when creating boxer '{name}': {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database by their ID.

    Args:
        boxer_id (int): The ID of the boxer to delete.

    Raises:
        ValueError: If no boxer with the given ID exists.
        sqlite3.Error: For unexpected database errors.
    """
    logger.info(f"Received request to delete boxer with ID: {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Successfully deleted boxer with ID: {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error when deleting boxer with ID {boxer_id}: {e}")
        raise e



def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves a leaderboard of boxers sorted by wins or win percentage.

    Args:
        sort_by (str, optional): The field to sort by. Must be "wins" or "win_pct".
                                 Defaults to "wins".

    Returns:
        List[dict[str, Any]]: A list of boxers with their stats, weight class,
                              and win percentage (as a percentage).

    Raises:
        ValueError: If an invalid sort_by value is provided.
        sqlite3.Error: For unexpected database errors.
    """
    logger.info(f"Received request to get leaderboard sorted by: {sort_by}")

    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort_by value received: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)
            }
            leaderboard.append(boxer)

        logger.info(f"Successfully retrieved leaderboard sorted by {sort_by} with {len(leaderboard)} boxers")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving leaderboard: {e}")
        raise e



def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the database by their ID.

    Args:
        boxer_id (int): The ID of the boxer to retrieve.

    Returns:
        Boxer: A Boxer object with the retrieved boxer's data.

    Raises:
        ValueError: If no boxer with the given ID exists.
        sqlite3.Error: For unexpected database errors.
    """
    logger.info(f"Received request to get boxer with ID: {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully retrieved boxer: {boxer.name} (ID: {boxer_id})")
                return boxer
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error when retrieving boxer with ID {boxer_id}: {e}")
        raise e



def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer from the database by their name.

    Args:
        boxer_name (str): The name of the boxer to retrieve.

    Returns:
        Boxer: A Boxer object with the retrieved boxer's data.

    Raises:
        ValueError: If no boxer with the given name exists.
        sqlite3.Error: For unexpected database errors.
    """
    logger.info(f"Received request to get boxer with name: {boxer_name}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully retrieved boxer: {boxer.name}")
                return boxer
            else:
                logger.warning(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error when retrieving boxer '{boxer_name}': {e}")
        raise e



def get_weight_class(weight: int) -> str:
    """Determines a boxer's weight class based on their weight.

    Args:
        weight (int): The boxer's weight in pounds.

    Returns:
        str: The name of the weight class.

    Raises:
        ValueError: If the weight is below the minimum valid weight (125 lbs).
    """
    logger.info(f"Determining weight class for weight: {weight}")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    logger.info(f"Assigned weight class: {weight_class} for weight: {weight}")
    return weight_class



def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates a boxer's stats with a win or loss.

    Args:
        boxer_id (int): The ID of the boxer to update.
        result (str): The result of the fight ("win" or "loss").

    Raises:
        ValueError: If the result is invalid or the boxer ID is not found.
        sqlite3.Error: For unexpected database errors.
    """
    logger.info(f"Received request to update stats for boxer ID {boxer_id} with result: {result}")

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: '{result}' for boxer ID {boxer_id}")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Successfully updated stats for boxer ID {boxer_id} with result: {result}")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating stats for boxer ID {boxer_id}: {e}")
        raise e

