import sqlite3
from os import path
from time import sleep


def infinite_retry(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Exception caught: {e}, retrying...")
                sleep(1)

    return wrapper



class Controller:
    """Controls all operations with sqlite database"""

    def __init__(self, db_name: str = "DB") -> None:
        """Creates db if it doesn't exist, connects to db
        Args:
            db_name (str, optional) Defaults to "MessageEvents".
        """
        self.sqlite_name = db_name
        if not path.exists(f"output\\{db_name}.sqlite"):
            self._create_db()
        self.conn = sqlite3.connect(
            f"output\\{db_name}.sqlite", check_same_thread=False
        )
        self.cursor = self.conn.cursor()


    def _create_db(self) -> None:
        """Private method, used to create and init db"""
        conn = sqlite3.connect(
            f"output\\{self.sqlite_name}.sqlite", check_same_thread=False
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE Users (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ChatID INTEGER,
                LimitPhotos INTEGER,
                UsedPhotos INTEGER
            )
        """
        )
    @infinite_retry
    def add_user(
        self,
        chat_id: int,
        limit_of_photos: int,
        used_photos: int
    ) -> None:
        sql = """
            INSERT INTO Users (
                ChatID,
                LimitPhotos,
                UsedPhotos
            ) VALUES (?, ?, ?)
        """

        self.cursor.execute(
            sql,
            (
                chat_id,
                limit_of_photos,
                used_photos
            ),
        )

        self.conn.commit()

    @infinite_retry
    def get_user_by_chat_id(self, user_chat_id: int) -> dict:
        """Returns dict with data about user where each key is a column name"""
        query = "SELECT * FROM Users WHERE ChatID = ?"
        self.cursor.execute(query, (user_chat_id,))
        result = self.cursor.fetchone()

        if result is None:
            return {}  # User not found

        # Convert the row into a dictionary
        columns = [description[0] for description in self.cursor.description]
        users_dict = {}
        for i, column in enumerate(columns):
            users_dict[column] = result[i]

        return users_dict
    
    @infinite_retry
    def update_limit_photos_by_chat_id(self, chat_id, limit_photos) -> None:
        """Update messages of user by chat_id"""

        query = "UPDATE Users SET LimitPhotos = ? WHERE ChatID = ?"
        self.cursor.execute(query, (limit_photos, chat_id))

        self.conn.commit()

    @infinite_retry
    def update_used_photos_by_chat_id(self, chat_id, used_photos) -> None:
        """Update messages of user by chat_id"""

        query = "UPDATE Users SET UsedPhotos = ? WHERE ChatID = ?"
        self.cursor.execute(query, (used_photos, chat_id))

        self.conn.commit()
