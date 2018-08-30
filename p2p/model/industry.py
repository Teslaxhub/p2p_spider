#!-*- coding:utf-8 -*-
from mysql_base import MysqlBase

class Industry(MysqlBase):
    __tablename__ = "p2p_industry_data"

    def get_by_time_sequences(self, time_sequences):
        where = 'time_sequences="%s"' % time_sequences
        for res in self._select(where=where):
            return res
        return None