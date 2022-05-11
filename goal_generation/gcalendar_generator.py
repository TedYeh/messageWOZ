import json
import random
from copy import deepcopy
from collections import Counter
import os
import numpy as np


class GcalendarGenerator:
    def __init__(self, database):
        self.database = database.values()
        #input()
        self.constraints2prob = {
            "是否全天": 0.5,
            "活動時間": 0.5
        }
        self.constraints2weight = {
            "是否全天": {'是': 1, '否': 5}
        }
        
        self.twodish_prob = 0.15
        self.all_attrs = ['名稱', '參加者', '活動內容', '活動地點', '是否全天', '活動時間']
        self.actions = ['search', 'create']
        

    def generate(self, goal_num=0, exist_goal=None, random_seed=None):
        name_flag = False
        if random_seed:
            random.seed(random_seed)
            np.random.seed(random_seed)
        act = np.random.choice(self.actions, p=[0.5, 0.5])
        goal = {
            "領域": "Calendar",
            "id": goal_num,
            "約束條件": [],
            "需求訊息": [],
            '預訂訊息': [],
            "生成方式": "",
            "動作": "建立一個活動" if act == 'create' else "查詢一個活動"
        }
        # generate method
        if exist_goal:
            goal['生成方式'] = 'id={}裡的{}'.format(exist_goal["id"], "郵件")
            goal['約束條件'].append(['名稱', '出現在id={}的{}裡'.format(exist_goal["id"], "郵件")])
            goal['需求訊息'].append(['活動時間', ""])
            name_flag = True
        else:
            goal['生成方式'] = '單領域生成'
        # generate constraints
        random_req = deepcopy(self.all_attrs)
        
        random_req.remove('名稱')
        random_req.remove('活動時間')
        
        random_req.remove('是否全天')    
        if not exist_goal and random.random() < self.constraints2prob['是否全天']:
            v = self.constraints2weight['是否全天']
            is_allday = random.choices(list(v.keys()), list(v.values()))[0]
            if is_allday == '是':
                goal['約束條件'] = [['是否全天', is_allday]]
                goal['需求訊息'].append(['名稱', ""])
                name_flag = True
        

        # generate required information
        if not name_flag:            
            goal['需求訊息'].append(['名稱', ""])
            goal['需求訊息'].append(['活動時間', ""])

        random.shuffle(random_req)
        req_num = random.choices([1, 2], [2, 3])[0]
        for k in random_req:
            if req_num > 0:
                goal['需求訊息'].append([k, ""])
                req_num -= 1
                #if k == '名稱':
                #    name_flag = True
            else:
                break

        return goal

def load_json(database_dir, filename):
    list_data = json.load(open(os.path.join(database_dir, filename), encoding='utf-8'))
    return {x[0]: x[1] for x in list_data}

if __name__ == "__main__":
    database = load_json('./', os.path.join('./', 'gcalendar_db.json'))
    tmp = GcalendarGenerator(database).generate()
    print(tmp)