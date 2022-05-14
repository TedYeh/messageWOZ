import json
import random
from copy import deepcopy
from collections import Counter
import os
import numpy as np


class GmailGenerator:
    def __init__(self, database):
        self.database = database.values()
        self.all_attrs = ['收件者', '寄件者', '郵件主旨', '內容']
        self.actions = ['search', 'create']
        

    def generate(self, goal_num=0, exist_goal=None, random_seed=None):
        name_flag = False
        if random_seed:
            random.seed(random_seed)
            np.random.seed(random_seed)
        act = np.random.choice(self.actions, p=[0.5, 0.5])
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
            random_req.remove('寄件者')
            random_req.remove('郵件主旨')
            random_req.remove('內容')
        else:
            random_req.remove('郵件主旨')

        # generate required information
        if not name_flag:
            if act == 'create':
                goal['需求訊息'].append(['收件者', ""])
                goal['需求訊息'].append(['郵件主旨', ""])
                goal['需求訊息'].append(['內容', ""])
                
            else:
                goal['需求訊息'].append(['郵件主旨', ""])

        random.shuffle(random_req)
        req_num = random.choices([1, 2], [2, 3])[0]
        for k in random_req:
            if req_num > 0:
                goal['需求訊息'].append([k, ""])
                req_num -= 1            
            else:
                break

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
            goal['需求訊息'].append(['訊息', ""])
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