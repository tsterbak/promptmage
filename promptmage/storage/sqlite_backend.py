"""This module contains the SQLiteBackend class, which is a subclass of the StorageBackend class. It is used to store the data in a SQLite database."""

import sqlite3
import json
from loguru import logger
from pathlib import Path
from typing import List

from promptmage.prompt import Prompt
from promptmage.exceptions import PromptNotFoundException
from promptmage.run_data import RunData
from promptmage.storage.storage_backend import StorageBackend


class SQLitePromptBackend(StorageBackend):
    """A class that stores the prompts in a SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database. Defaults to ".promptmage/promptmage.db".
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path if db_path else ".promptmage/promptmage.db"
        self._init_db()
        self._create_table()

    def _init_db(self):
        """Create the database if it doesn't exist."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Error connecting to SQLite database: {e}")
        finally:
            if conn:
                conn.close()

    def _create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS prompts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            system TEXT NOT NULL,
            user TEXT NOT NULL,
            version INTEGER NOT NULL,
            template_vars TEXT NOT NULL
        );
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()

    def store_prompt(self, prompt: Prompt):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO prompts VALUES (?, ?, ?, ?, ?, ?)",
                (
                    prompt.id,
                    prompt.name,
                    prompt.system,
                    prompt.user,
                    prompt.version,
                    ",".join(prompt.template_vars),
                ),
            )
            conn.commit()

    def get_prompt(self, prompt_name: str) -> Prompt:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompts WHERE name=?", (prompt_name,))
            rows = cursor.fetchall()
            if len(rows) == 0:
                raise PromptNotFoundException(
                    f"Prompt with name {prompt_name} not found."
                )
            # select the latest version
            row = sorted(rows, key=lambda row: row[4], reverse=True)[0]
            return Prompt(
                id=row[0],
                name=row[1],
                system=row[2],
                user=row[3],
                version=row[4],
                template_vars=row[5].split(","),
            )

    def get_prompts(self) -> List[Prompt]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompts")
            rows = cursor.fetchall()
            prompts = []
            for row in rows:
                prompts.append(
                    Prompt(
                        id=row[0],
                        name=row[1],
                        system=row[2],
                        user=row[3],
                        version=row[4],
                        template_vars=row[5].split(","),
                    )
                )
            return prompts

    def delete_prompt(self, prompt_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prompts WHERE id=?", (prompt_id,))
            conn.commit()


class SQLiteDataBackend(StorageBackend):
    """A class that stores the data in a SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database. Defaults to ".promptmage/promptmage.db".
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path if db_path else ".promptmage/promptmage.db"
        self._init_db()
        self._create_table()

    def _init_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Error connecting to SQLite database: {e}")
        finally:
            if conn:
                conn.close()

    def _create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS data (
            step_run_id TEXT PRIMARY KEY,
            run_time TEXT NOT NULL,
            step_name TEXT NOT NULL,
            run_id TEXT,
            status TEXT NOT NULL,
            prompt TEXT,
            input_data TEXT,
            output_data TEXT
        );
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()

    def store_data(self, run_data: RunData):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run_data.step_run_id,
                    run_data.run_time,
                    run_data.step_name,
                    run_data.run_id,
                    run_data.status,
                    json.dumps(run_data.prompt.to_dict()) if run_data.prompt else None,
                    json.dumps(run_data.input_data),
                    json.dumps(run_data.output_data),
                ),
            )
            conn.commit()

    def get_data(self, step_run_id: str) -> RunData:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data WHERE step_run_id=?", (step_run_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return RunData(
                step_run_id=row[0],
                run_time=row[1],
                step_name=row[2],
                run_id=row[3],
                status=row[4],
                prompt=Prompt.from_dict(json.loads(row[5])) if row[5] else None,
                input_data=json.loads(row[6]),
                output_data=json.loads(row[7]),
            )

    def get_all_data(self) -> List[RunData]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data")
            rows = cursor.fetchall()
            run_data = []
            for row in rows:
                r = RunData(
                    step_run_id=row[0],
                    run_time=row[1],
                    step_name=row[2],
                    run_id=row[3],
                    status=row[4],
                    prompt=Prompt.from_dict(json.loads(row[5])) if row[5] else None,
                    input_data=json.loads(row[6]),
                    output_data=json.loads(row[7]),
                )
                run_data.append(r)

            return run_data
