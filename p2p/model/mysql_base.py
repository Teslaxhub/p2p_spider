#!-*- coding:utf-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from basedb import BaseDB
import mysql.connector

class MysqlBase(BaseDB):
    __tablename__ = ""
    placeholder = '%s'

    def __init__(self, host='localhost', port=3306, database='resultdb',
                 user='root', passwd=None):
        self.database_name = 'p2p_spider'
        self.conn = mysql.connector.connect(
            host="",
            port='',
            user=0000,
            password='',
            database=self.database_name,
            autocommit=True,
            charset="utf8",
        )

    @property
    def dbcur(self):
        try:
            if self.conn.unread_result:
                self.conn.get_rows()
            return self.conn.cursor()
        except (mysql.connector.OperationalError, mysql.connector.InterfaceError):
            self.conn.ping(reconnect=True)
            self.conn.database = self.database_name
            return self.conn.cursor()
