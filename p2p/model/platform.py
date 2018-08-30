#!-*- coding:utf-8 -*-
from mysql_base import MysqlBase

class Platform(MysqlBase):
    __tablename__ = "p2p_platform_data"

    def value_filter(self, params):
        """返回对应value为空的字段"""
        assert params and isinstance(params, dict)
        filter_keys = ["newmoney", "moneyinout", "newuser_count",
                       "olduser_money", "olduser_count", "newuser_money"]
        filtered_keys = []
        for key in filter_keys:
            if not params.get(key):
                filtered_keys.append(key)
        return filtered_keys

    def get_by_plat_time(self, platform_name, time_squences):
        where = 'platform_name="%s" and time_sequences="%s"' % (platform_name, time_squences)
        for result in self._select2dic(where=where):
            return result
        return None

    def save(self, **kwargs):
        return self._insert(**kwargs)

    def check_for_update_by_plat_time(self, platform_name, time_squences, params):
        """天眼为空直接插入，若已存在，则更新为0、空值"""
        result = self.get_by_plat_time(platform_name, time_squences)
        where = 'platform_name="%s" and time_sequences="%s"' % (platform_name, time_squences)
        if not result:  # 为空则直接插入
            return self._insert(**params)
        else:
            update_params_dic = {}
            filtered_keys = self.value_filter(result)
            for key in filtered_keys:   # 天眼为空&之家不为空，则update
                if params.get(key):
                    update_params_dic[key] = params.get(key)
            if update_params_dic:
                print 'update plat info\tplatform_name=%s\twhere=%s\tvalue=%s' % (platform_name, where, update_params_dic)
                self._update(where=where, **update_params_dic)

if __name__ == "__main__":
    p = Platform()
    data={
        'newmoney': 414.0, 'time_sequences': u'2017-10-28', 'newuser_count': 94,
        'olduser_count': 3, 'newuser_money': 408.0, 'olduser_money': 6.0,
        "platform_name":"为为贷"
    }
    # p.check_for_update_by_plat_time(data.get('platform_name'), data.get('time_sequences'), data)
    # exit()
    def _test_select():
        parsed_info = {
            "platform_name": '有利网',
            "time_sequences": '2018-05-01'
        }
        where = 'platform_name="%s" and time_sequences="%s"' % \
                (parsed_info.get('platform_name'), parsed_info.get('time_sequences'))
        generator_result = p._select2dic(where=where, limit=1)
        for result in generator_result:
            import json
            print json.dumps(result.keys())

    def _test_insert():
        data = {
            "newmoney":58844083.42,
            "time_sequences": '2018-08-28',
            "platform_name": 'PPmoney网贷',
            "plat_official_url": 'www.ppmoney.com',
            "moneyinout": 11724352.08
        }
        p._insert(**data)

    def test_update():
        data={
            'newmoney': 414.0, 'time_sequences': u'2017-10-28', 'newuser_count': 94,
            'olduser_count': 3, 'newuser_money': 408.0, 'olduser_money': 6.0,
            "platform_name":"为为贷"
        }
        parsed_info = {
            "platform_name": '为为贷',
            "time_sequences": '2017-10-28'
        }
        where = 'platform_name="%s" and time_sequences="%s"' % \
                (parsed_info.get('platform_name'), parsed_info.get('time_sequences'))
        return p._update(where=where, **data)
    c = test_update()
    if isinstance(c, classmethod):
        print 'yes'

    # print c
    # print type(c)
