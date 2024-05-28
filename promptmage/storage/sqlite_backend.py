"""This module contains the SQLiteBackend class, which is a subclass of the StorageBackend class. It is used to store the data in a SQLite database."""

import sqlite3
import json
from loguru import logger
from typing import List, Dict

from promptmage.prompt import Prompt
from promptmage.run_data import RunData
from promptmage.storage.storage_backend import StorageBackend


class SQLitePromptBackend(StorageBackend):
    """A class that stores the prompts in a SQLite database."""

    def __init__(self, db_path: str = "promptmage.db"):
        self.db_path = db_path
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
            row = cursor.fetchone()
            if row is None:
                return None
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


class SQLiteDataBackend(StorageBackend):
    """A class that stores the data in a SQLite database."""

    def __init__(self, db_path: str = "promptmage.db"):
        self.db_path = db_path
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
            run_id TEXT PRIMARY KEY,
            run_time TEXT NOT NULL,
            step_name TEXT NOT NULL,
            prompt TEXT NOT NULL,
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
                "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?)",
                (
                    run_data.run_id,
                    run_data.run_time,
                    run_data.step_name,
                    json.dumps(run_data.prompt.to_dict()),
                    json.dumps(run_data.input_data),
                    json.dumps(run_data.output_data),
                ),
            )
            conn.commit()

    def get_data(self, run_id: str) -> RunData:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data WHERE run_id=?", (run_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return RunData(
                run_id=row[0],
                run_time=row[1],
                step_name=row[2],
                prompt=Prompt.from_dict(json.loads(row[3])),
                input_data=json.loads(row[4]),
                output_data=json.loads(row[5]),
            )

    def get_all_data(self) -> Dict[str, RunData]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data")
            rows = cursor.fetchall()
            run_data = {}
            for row in rows:
                run_data[row[0]] = RunData(
                    run_id=row[0],
                    run_time=row[1],
                    step_name=row[2],
                    prompt=Prompt.from_dict(json.loads(row[3])),
                    input_data=json.loads(row[4]),
                    output_data=json.loads(row[5]),
                ).to_dict()

            return run_data
