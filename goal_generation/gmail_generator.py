import json
import random
from copy import deepcopy
from collections import Counter
import os
import numpy as np


class GmailGenerator:
    def __init__(self, database):
        self.database = database.values()
        #input()
        #self.constraints2prob = {
        #    "名称": 0.1,
        #    "推荐菜": 0.6,
        #    "人均消费": 0.5,
        #    "评分": 0.5
        #}
        #self.constraints2weight = {
        #    "名称": dict.fromkeys([x['名称'] for x in self.database], 1),
        #    "推荐菜": {1: 5, 2: 1},
        #    "人均消费": {"50元以下": 1,
        #             "50-100元": 15,
        #             "100-150元": 15,
        #             "150-500元": 5,
        #             "500-1000元": 2,
        #             "1000元以上": 1
        #             },
        #    "评分": {'4分以上': 0.2, '4.5分以上': 0.6, '5分': 0.2}
        #}
        #self.min_constraints = 1
        #self.max_constraints = 3
        #self.min_require = 1
        #self.max_require = 3
        #self.order_prob = 0.1
        self.twodish_prob = 0.15
        self.all_attrs = ['收件者', '寄件者', '郵件主旨', '內容']
        self.actions = ['search', 'create']
        #self.cooccur = {}  # check if the list is empty
        #for res in self.database:
        #    for dish in res['推荐菜']:
        #        self.cooccur[dish] = self.cooccur.get(dish, set()).union(set(res['推荐菜']))
        #        self.cooccur[dish].remove(dish)
        #all_dish = [dish for res in self.database for dish in res['推荐菜']]
        #all_dish = Counter(all_dish)
        #for k,v in all_dish.items():
        #    if v==1:
        #        del self.cooccur[k]
        #self.time2weight = {}
        #for hour in range(0, 23):
        #    for minute in [':00', ':30']:
        #        timePoint = str(hour) + minute
        #        if hour in [11, 12, 17, 18]:  # 饭点
        #            self.time2weight[timePoint] = 20
        #        elif hour in list(range(0, 7)):  # 深夜/清晨
        #            self.time2weight[timePoint] = 1
        #        else:  # 白天非饭点
        #            self.time2weight[timePoint] = 5

    def generate(self, goal_num=0, exist_goal=None, random_seed=None):
        name_flag = False
        if random_seed:
            random.seed(random_seed)
            np.random.seed(random_seed)
        act = np.random.choice(self.actions)
        goal = {
            "領域": "Gmail",
            "id": goal_num,
            "約束條件": [],
            "需求訊息": [],
            '預訂訊息': [],
            "生成方式": "",
            "動作": "寄一封郵件" if act == 'create' else "查詢一封郵件"
        }
        # generate method
        if exist_goal:
            goal['生成方式'] = 'id={}裡的{}'.format(exist_goal["id"], "行事曆")
            goal['約束條件'].append(['信件主旨', '出現在id={}的{}裡'.format(exist_goal["id"], "行事曆")])
            name_flag = True
        else:
            goal['生成方式'] = '單領域生成'
        # generate constraints
        random_req = deepcopy(self.all_attrs)
        if act == 'create':
            random_req.remove('收件者')
            random_req.remove('郵件主旨')
            random_req.remove('內容')
        # if constraint == name ?
        #if not exist_goal and random.random() < self.constraints2prob['名称']:
        #    v = self.constraints2weight['名称']
        #    goal['约束条件'] = [['名称', random.choices(list(v.keys()), list(v.values()))[0]]]
        #    name_flag = True
        #
        #else:
        #    rest_constraints = list(self.constraints2prob.keys())
        #    rest_constraints.remove('名称')
        #    random.shuffle(rest_constraints)
        #    # cons_num = random.randint(self.min_constraints, self.max_constraints)
        #    cons_num = random.choices([1, 2, 3], [20, 60, 20])[0]
        #    for k in rest_constraints:
        #        if cons_num > 0:
        #            v = self.constraints2weight[k]
        #            if k == '推荐菜':
        #                value = random.choices(list(self.cooccur.keys()))
        #                if random.random() < self.twodish_prob and self.cooccur[value[0]]:
        #                    value.append(random.choice(list(self.cooccur[value[0]])))
        #            else:
        #                value = random.choices(list(v.keys()), list(v.values()))[0]
        #            goal['约束条件'].append([k, value])
        #            random_req.remove(k)
        #            cons_num -= 1
        #        else:
        #            break

        # generate required information
        if not name_flag:
            if act == 'create':
                goal['需求訊息'].append(['收件者', ""])
                goal['需求訊息'].append(['郵件主旨', ""])
                goal['需求訊息'].append(['內容', ""])
            #else:
            #    goal['需求訊息'].append(['郵件主旨', ""])

        random.shuffle(random_req)
        req_num = random.choices([1, 2], [30, 70])[0]
        for k in random_req:
            if req_num > 0:
                goal['需求訊息'].append([k, ""])
                req_num -= 1
                if k == '收件者':
                    name_flag = True
            else:
                break



        # if random.random() < self.order_prob:
        #     people_num = random.randint(1, 9)
        #     week_day = random.choice(['周日', '周一', '周二', '周三', '周四', '周五', '周六', ])
        #     book_time = random.choices(list(self.time2weight.keys()), list(self.time2weight.values()))[0]
        #     goal['预订信息'] = [["人数", people_num], ["日期", week_day], ["时间", book_time]]
        #     goal['需求信息'].append(["预订订单号", ""])

        return goal

class MessageGenerator:
    def __init__(self):
        self.all_attrs = ['使用者', '訊息']
        self.actions = ['create']

    def generate(self, goal_num=0, exist_goal=None, random_seed=None):
        name_flag = False
        if random_seed:
            random.seed(random_seed)
            np.random.seed(random_seed)
        act = np.random.choice(self.actions)
        goal = {
            "領域": "Message",
            "id": goal_num,
            "約束條件": [],
            "需求訊息": [],
            '預訂訊息': [],
            "生成方式": "",
            "動作": "寄一則訊息"
        }
        # generate method
        if exist_goal:
            goal['生成方式'] = 'id={}裡的{}'.format(exist_goal["id"], "郵件")
            goal['約束條件'].append(['使用者', '出現在id={}的{}裡'.format(exist_goal["id"], "郵件")])
            name_flag = True
        else:
            goal['生成方式'] = '單領域生成'

        goal['需求訊息'].append(['使用者', ""])
        goal['需求訊息'].append(['訊息', ""])

        return goal

def load_json(database_dir, filename):
    list_data = json.load(open(os.path.join(database_dir, filename), encoding='utf-8'))
    return {x[0]: x[1] for x in list_data}

if __name__ == "__main__":
    database = load_json('./', os.path.join('./', 'gmail_db.json'))
    tmp = GmailGenerator(database).generate()
    print(tmp)