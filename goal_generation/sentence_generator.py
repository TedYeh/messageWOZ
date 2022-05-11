# -*- coding: utf-8 -*-
import random
from pprint import pprint
import numpy as np
import json
import datetime
from goal_generation import GoalGenerator

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
            # if "周边" in goal["生成方式"]:
            #     sen += goal["生成方式"] + "。" + "通过它的周边推荐，"
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

                #for constraint in goal["约束条件"]:
                #    if constraint[0] == "酒店类型":
                #        sen += ('你希望酒店是%s的。' % constraint[1])
                #    elif "酒店设施" in constraint[0]:
                #        sen += ('你希望酒店提供%s。' % constraint[0].split('-')[1])
                #    elif constraint[0] == "价格":
                #        sen += ('你希望酒店的最低价格是%s的。' % constraint[1])
                #    elif constraint[0] == "评分":
                #        sen += ('你希望酒店的评分是%s。' % constraint[1])
                #    elif constraint[0] == "预订信息":
                #        sen += ""
                # if goal["预订信息"]:
                #     sen += "你希望预订在%s入住，共%s人，住%s天。" % (goal["预订信息"][1][1], goal["预订信息"][0][1], goal["预订信息"][2][1])
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
                        #print(sen)
                #    elif constraint[0] == "游玩时间":
                #        sen += ('你希望游玩的时长是%s。' % constraint[1])
                #    elif constraint[0] == "评分":
                #        sen += ('你希望景点的评分是%s。' % constraint[1])
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
            #    for constraint in goal["约束条件"]:
            #        if constraint[0] == "名称":
            #            if '周边' in constraint[1]:
            #                origin_id = int(constraint[1].split('id=')[1][0])
            #                sen += ('你要去id=%d附近的餐馆(id=%d)用餐。' % (origin_id, goal['id']))
            #            else:
            #                sen += ('你要去名叫%s的餐馆(id=%d)用餐。' % (constraint[1], goal['id']))
            #    if sen == '':
            #        sen += "你要去一个餐馆(id=%d)用餐。" % goal['id']
#
            #    for constraint in goal["约束条件"]:
            #        if constraint[0] == "推荐菜":
            #            sen += ('你想吃的菜肴是%s。' % '、'.join(constraint[1]))
            #        elif constraint[0] == "人均消费":
            #            sen += ('你希望餐馆的人均消费是%s的。' % constraint[1])
            #        elif constraint[0] == "评分":
            #            sen += ('你希望餐馆的评分是%s。' % constraint[1])
                # if goal["预订信息"]:
                #     sen += "你希望预订在%s%s共%s人一起用餐。" % (goal["预订信息"][1][1], goal["预订信息"][2][1], goal["预订信息"][0][1])
             
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
    sg = {'領域':'', 'id':None, '約束條件':[], "需求訊息":[], '生成方式':'' }
    goals = []
    for i in range(1, 100+1):
        main_goal = {'goals':[], "description":[], "timestamp":'', "ID":None}
        semantic_tuples, goal_list = GoalGenerator.generate()    
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
    json_object = json.dumps(goals, indent = 4)
  
    # Writing to sample.json
    with open("goal_example.json", "w") as outfile:
        outfile.write(json_object)