#!/usr/bin/env python3
""" log message obfuscated using regex """
import mysql.connector
from mysql.connector.connection import MySQLConnection
from typing import List
import logging
import re
import os

PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(
        fields: List[str],
        redaction: str,
        message: str,
        separator: str) -> str:
    """ This function uses a regex to replace occurrences of certain fields.
    """
    for f in fields:
        message = re.sub(f'{f}=.*?{separator}', f'{f}={redaction}{separator}',
                         message, count=1)
    return message


def get_logger() -> logging.Logger:
    """ create logger and return back """
    logger = logging.Logger("user_data", logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(handler)
    return logger


def get_db() -> MySQLConnection:
    """ connect to db and return connection object """
    host = os.environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    username = os.environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    db_name = os.environ.get("PERSONAL_DATA_DB_NAME")
    return MySQLConnection(user=username, password=password, host=host,
                           database=db_name)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self._fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ format the log record """
        record.msg = filter_datum(self._fields, self.REDACTION, record.msg,
                                  self.SEPARATOR)
        return super().format(record)


def main():
    """ The main program """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    fields = ('name', 'email', 'phone', 'ssn', 'password', 'ip', 'last_login',
              'user_agent')
    logger = get_logger()
    for row in cursor:
        user = ''.join([f'{k}={v};' for k, v in zip(fields, row)])
        logger.info(user)
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
    