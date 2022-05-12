# -*- coding: utf-8 -*-
import random
from pprint import pprint
import numpy as np
import json
import datetime
from goal_generation import GoalGenerator
import argparse

class SentenceGenerator:
    def generate(self, goals, random_seed=None):
        sens = []
        if random_seed:
            random.seed(random_seed)
            np.random.seed(random_seed)
        # print(goals)
        # for ls in goals:
        for goal in goals:
            # print(goal)
            sen = ''
            domain = goal["領域"]
            if domain == "Gmail":
                for constraint in goal["約束條件"]:
                    if constraint[0] == "信件主旨":
                        if '裡' in constraint[1]:
                            origin_id = int(constraint[1].split('id=')[1][0])
                            if goal['動作'] == '寄一封郵件':
                                sen += ('你要寄一封主旨包含id=%d名稱的(id=%d)信件。' % (origin_id, goal['id']))
                            else:
                                sen += ('你要找一封主旨包含id=%d名稱的(id=%d)信件。' % (origin_id, goal['id']))
                        else:
                            if goal['動作'] == '寄一封郵件':
                                sen += ('你要寄一封主旨叫%s的信件(id=%d)。' % (constraint[1], goal['id']))
                            else:sen += ('你要找一封主旨叫%s的信件(id=%d)。' % (constraint[1], goal['id']))
                if sen == '':
                    if goal['動作'] == '寄一封郵件':
                        sen += "你要寄一封信(id=%d)。" % goal['id']
                    else: sen += "你要找一封信(id=%d)。" % goal['id']

            elif domain == "Calendar":
                for constraint in goal["約束條件"]:
                    if constraint[0] == "名稱":
                        if '裡' in constraint[1]:
                            origin_id = int(constraint[1].split('id=')[1][0])
                            if goal['動作'] == '建立一個活動':
                                sen += ('你要建立名稱包含id=%d信件主旨的(id=%d)活動。' % (origin_id, goal['id']))
                            else:sen += ('你要查詢名稱包含id=%d信件主旨的(id=%d)活動。' % (origin_id, goal['id']))
                        else:
                            if goal['動作'] == '建立一個活動':
                                sen += ('你要建立名叫%s的活動(id=%d)。' % (constraint[1], goal['id']))
                            else:sen += ('你要找名叫%s的活動(id=%d)。' % (constraint[1], goal['id']))
                if sen == '':
                    if goal['動作'] == '建立一個活動':
                        sen += "你要建立一個活動(id=%d)。" % goal['id']
                    else: sen += "你要找一個活動(id=%d)。" % goal['id']

                for constraint in goal["約束條件"]:
                    if constraint[0] == "是否全天":
                        sen += ('你希望這個活動%s全天的。' % ('是' if constraint[1]=='是' else '不是'))
            elif domain == "Message":
                for constraint in goal["約束條件"]:
                    if constraint[0] == "使用者":
                        if '裡' in constraint[1]:
                            origin_id = int(constraint[1].split('id=')[1][0])
                            if goal['動作'] == '寄一則訊息':
                                sen += ('你要寄一則有id=%d收件者的(id=%d)訊息。' % (origin_id, goal['id']))
                        else:
                            if goal['動作'] == '寄一則訊息':
                                sen += ('你要寄一封主旨叫%s的信件(id=%d)。' % (constraint[1], goal['id']))
                if sen == '':
                    if goal['動作'] == '寄一則訊息':
                        sen += "你要寄一則訊息(id=%d)。" % goal['id']
            
            if domain == 'Gmail': d = '郵件'
            elif domain == 'Calendar': d = '活動' 
            else: d = '訊息'
            if '查詢' in goal['動作'] or '找' in goal['動作']:
                sen += '你想知道這個%s的%s。' % (d, '、'.join(["酒店设施是否包含%s" % item[0].split('-')[1]
                                                       if "酒店设施" in item[0] 
                                                       else item[0]
                                                       for item in goal['需求訊息']]))
            else: 
                sen += '你要填入這個%s的%s。' % (d, '、'.join(["酒店设施是否包含%s" % item[0].split('-')[1]
                                                       if "酒店设施" in item[0]
                                                       else item[0]
                                                       for item in goal['需求訊息']]))
            sens.append(sen)
        return sens

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=int, default=100)
    args = parser.parse_args()
    sg = {'領域':'', 'id':None, '約束條件':[], "需求訊息":[], '生成方式':'' }
    goals = []

    for i in range(args.num):
        main_goal = {'goals':[], "description":[], "timestamp":'', "ID":None}
        semantic_tuples, goal_list = GoalGenerator.generate(single_domain=False, cross_domain=True, multi_target=True)    
        #print(goal_list)
        sens = SentenceGenerator().generate(goal_list)
        for goal in goal_list:
            del goal['動作']
        main_goal['goals'] = goal_list
        main_goal['description'] = sens
        main_goal['timestamp'] = str(datetime.datetime.now())
        main_goal['ID'] = i
        goals.append(main_goal)
        pprint(main_goal)
    
    random.shuffle(goals)
    #json_object = json.dumps(goals, indent = 4, ensure_ascii=False)
  
    # Writing to sample.json
    with open("../data_labelling/results/input/goal_task.json", "w", encoding='utf-8') as f:json.dump(goals, f, indent = 5, ensure_ascii=False)