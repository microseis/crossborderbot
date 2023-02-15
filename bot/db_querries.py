import pymysql
import os


class DbQueries:
    def __init__(self):
        """Db connection"""
        self.connection = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            passwd=os.environ.get("DB_PASSWD"),
            database=os.environ.get("DB_NAME"),
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

        self.cursor = self.connection.cursor()

    def account_exist(self, user_id):
        """Checking account existence in database"""
        with self.connection:
            self.connection.ping()
            result = self.cursor.execute(
                'SELECT * FROM accounts WHERE user_id ="%s"', user_id
            )
            return bool(result)

    def add_account(self, user_id, account_name, account_pwd):
        """Adding new account"""
        with self.connection:
            self.connection.ping()
            return self.cursor.execute(
                "INSERT INTO accounts (`user_id`, `account_name`, `passwd`) VALUES (%s, %s, %s)",
                (user_id, account_name, account_pwd),
            )

    def is_unique(self, account_name):
        """Checking account name uniqueness"""
        with self.connection:
            self.connection.ping()
            result = self.cursor.execute(
                'SELECT * FROM accounts WHERE account_name ="%s"', account_name
            )
            return bool(result)

    def update_work(self, user_id, status):
        """Updating work status"""
        with self.connection:
            self.connection.ping()
            result = self.cursor.execute(
                "UPDATE accounts SET work_is_submitted = %s WHERE user_id = %s",
                (status, user_id),
            )
            return result

    def check_work(self, user_id):
        """Checking work existence in database"""
        with self.connection:
            self.connection.ping()
            result = self.cursor.execute(
                "SELECT work_is_submitted FROM accounts WHERE user_id = %s", (user_id)
            )
            return result

    def set_filename(self, filename, user_id):
        with self.connection:
            self.connection.ping()
            return self.cursor.execute(
                "INSERT INTO accounts (filename) VALUES (%s) WHERE user_id = %s",
                (filename, user_id),
            )

    def update_filename(self, filename, user_id):
        with self.connection:
            self.connection.ping()
            return self.cursor.execute(
                "UPDATE accounts SET filename = %s WHERE user_id =%s",
                (filename, user_id),
            )

    def select_account_name(self, user_id):
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                'SELECT account_name FROM accounts WHERE user_id ="%s"', user_id
            )
            records = self.cursor.fetchone()
            return records["account_name"]

    def select_counter(self, user_id):
        with self.connection:
            self.connection.ping()
            self.cursor.execute(
                'SELECT counter FROM accounts WHERE user_id ="%s"', user_id
            )
            records = self.cursor.fetchone()
            return records["counter"]
