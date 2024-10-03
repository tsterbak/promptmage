import sqlite3
import json
from loguru import logger


def backup_db_to_json(db_path: str, json_path: str):
    """Backup a SQLite database to a JSON file.

    Args:
        db_path (str): Path to the SQLite database file.
        json_path (str): Path to the JSON file to save the backup to.
    """
    logger.info(f"Backing up database from '{db_path}' to '{json_path}' ...")
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get a list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Dictionary to hold the database structure
    db_dict = {}

    for table_name in tables:
        table_name = table_name[0]

        # Get the table's data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names and types
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [
            (description[1], description[2]) for description in cursor.fetchall()
        ]  # (name, type)

        # Add table data to the dictionary
        db_dict[table_name] = {
            "columns": columns,  # Store both column name and type
            "data": rows,
        }

    # Close the connection
    conn.close()

    # Write the database dictionary to a JSON file
    with open(json_path, "w") as json_file:
        json.dump(db_dict, json_file, indent=4)
    logger.info("Backup complete.")


def restore_db_from_json(db_path: str, json_path: str):
    """Restore a SQLite database from a JSON file.

    Args:
        db_path (str): Path to the SQLite database file.
        json_path (str): Path to the JSON file containing the database backup.
    """
    logger.info(f"Restoring database from '{json_path}' to '{db_path}' ...")
    # Read the JSON file
    with open(json_path, "r") as json_file:
        db_dict = json.load(json_file)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if they exist (optional, use with caution)
    for table_name in db_dict.keys():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Create tables and insert data
    for table_name, table_data in db_dict.items():
        columns = table_data["columns"]  # List of (name, type) tuples
        column_definitions = ", ".join(
            [f"{col_name} {col_type}" for col_name, col_type in columns]
        )

        # Create table with the correct column types
        cursor.execute(f"CREATE TABLE {table_name} ({column_definitions})")

        # Insert rows
        for row in table_data["data"]:
            placeholders = ", ".join(["?" for _ in columns])
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    logger.info("Restore complete.")
