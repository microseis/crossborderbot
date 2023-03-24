import os

import pymysql


class DbQueries:
    def __init__(self):
        """Db connection"""
        self.connection = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            passwd=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

        self.cursor = self.connection.cursor()

    def account_exist(self, user_id: int) -> bool:
        """Checking account existence in database.
        :param user_id: идентификатор пользователя"""

        with self.connection:
            self.connection.ping()
            result = self.cursor.execute(
                'SELECT * FROM accounts WHERE user_id ="%s"', user_id
            )
            return bool(result)

    def add_account(self, user_id: int, account_name: str, account_pwd: str) -> None:
        """Метод добавления нового аккаунта.
        :param user_id: Идентификатор пользователя
        :param account_pwd: Пароль для создаваемого аккаунта
        :param account_name: Название создаваемого аккаунта"""
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                "INSERT INTO accounts (`user_id`, `account_name`, `passwd`) VALUES (%s, %s, %s)",
                (user_id, account_name, account_pwd),
            )

    def is_unique(self, account_name: str) -> bool:
        """Проверка названия аккаунта на уникальность.
        :param account_name: Название аккаунта
        :return: True если аккаунт с таким названием уже существует."""
        with self.connection:
            self.connection.ping()
            result = self.cursor.execute(
                'SELECT * FROM accounts WHERE account_name ="%s"', account_name
            )
            return bool(result)

    def update_work(self, user_id: int, status: bool) -> None:
        """Updating work status"""
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                "UPDATE accounts SET work_is_submitted = %s WHERE user_id = %s",
                (status, user_id),
            )

    def check_work(self, user_id: int):
        """Checking work existence in database"""
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                "SELECT work_is_submitted FROM accounts WHERE user_id = %s", user_id
            )

    def set_filename(self, filename: str, user_id: int) -> None:
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                "INSERT INTO accounts (filename) VALUES (%s) WHERE user_id = %s",
                (filename, user_id),
            )

    def update_filename(self, filename: str, user_id: int) -> None:
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                "UPDATE accounts SET filename = %s WHERE user_id =%s",
                (filename, user_id),
            )

    def select_account_name(self, user_id: int) -> str:
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                'SELECT account_name FROM accounts WHERE user_id ="%s"', user_id
            )
            records = self.cursor.fetchone()
            return records[0]

    def select_counter(self, user_id: int) -> str:
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                'SELECT counter FROM accounts WHERE user_id ="%s"', user_id
            )
            records = self.cursor.fetchone()
            return records[0]
