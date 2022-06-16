# "你要查詢一個{event}。你希望{event}{event_allDay}。你想知道這個{event}的{name||time||participant||content||location}"
# "你要查詢一個{mail}。你想知道這個{mail}的{receiver||sender||subject||content}"
# "你要查詢一個{mail}。你希望{receiver}有出現在(id)裡的{participant}。你想知道{mail}的{sender||subject||content}。"
# "你要查詢一個{event}。你希望{participant}有出現在(id)裡的{receiver}。你想知道{mail}的{name||time||participant||content||location}"
# "你要{build}一個{event}。你想知道這個{mail}的{receiver}||{sender}||{subject}||{content}"
# "你要{send}一則{receiver||subject||content}為{}的{mail}給(id)裡的{participant}。請填妥{receiver||subject||content}"
# "你要{send}一則{message}給(id)裡的{receiver}"
# "你要{send}一則{message}給(id)裡的{participant}"
# "你要{send}一則{message}給{receiver}"
import random
import os
import json
import numpy as np
from pprint import pprint
from copy import deepcopy
from gcalendar_generator import GcalendarGenerator
from gmail_generator import GmailGenerator, MessageGenerator

domains = ['活動', '郵件', '訊息']
actions = ['search', 'create']
slots = {'活動':['名稱', '時間', '參加者', '內容', '地點'], '郵件':['收件者', '寄件者', '主旨', '內容'], '訊息':['收件者', '內容', '應用程式']} 
domain_types = ['單領域', '多領域']
goal_num = 0
goal_max = 3
id = 0
# 你要{action[0]}一個{domain}。你想知道這個{domain}的{slot}
# other = '郵件' if domain == '活動' else '郵件'
# 你要{action[0]}一個{domain}。你希望{slot['活動'][2]||slot[domain][0]}有出現在id = {id}裡的{slot[other][2]||slot[other][0]}
# 你要{action[1]}一個{domain}給{}。

class GoalGenerator:
    @staticmethod
    def generate(single_domain=False, cross_domain=True, multi_target=True):
        goal_list = generate_method(
            database_dir=os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),'./database/')),
            single_domain=single_domain, cross_domain=cross_domain, multi_target=True
        )
        #goal_list = goals_reorder(goal_list)
        #print('goal_list', goal_list)
        semantic_tuples = []
        for sub_goal in goal_list:
            sub_goal_id = sub_goal['id']
            domain = sub_goal['領域']
            for slot, value in sub_goal['約束條件']:
                semantic_tuples.append([sub_goal_id, domain, slot, value, False])
            for slot, value in sub_goal['需求訊息']:
                if '周边' in slot or slot=='推荐菜':
                    value = []
                semantic_tuples.append([sub_goal_id, domain, slot, value, False])
        return semantic_tuples, goal_list


def call_count():
    global goal_num
    goal_num += 1
    return goal_num

class SingleDomainGenerator():
    def __init__(self, database, domain_index=None):
        self.database = database
        self.gmail_generator = GmailGenerator(database['gmail'])
        self.gcalendar_generator = GcalendarGenerator(database['gcalendar'])
        self.message_generator = MessageGenerator()
        self.generators = [self.gmail_generator, self.gcalendar_generator, self.message_generator]#, self.hotel_generator
        if domain_index:
            self.generators = [self.generators[domain_index - 1]]

    def generate(self, multi_target=False):
        goal = []
        # 单领域单目标，保证一定会有一个目标生成
        if not multi_target and len(self.generators) == 1:
            goal.append(self.generators[0].generate(call_count()))
        else:
            random.shuffle(self.generators)
            for generator in self.generators:
                # 多领域单独生成，每个领域中目标以一定概率独立生成
                if len(goal) == goal_max:
                        break
                if random.random() < 0.55:
                    goal.append(generator.generate(call_count()))
                    # 多领域多目标生成，控制总数不超过3
                    if len(goal) == goal_max:
                        break
                    if multi_target and random.random() < 0.15:
                        goal.append(generator.generate(call_count()))

            if len(goal) == 0:
                goal.append(self.generators[0].generate(call_count()))
        assert 0 < len(goal) <= goal_max
        return goal

class CrossDomainGenerator():
    def __init__(self, database):
        self.database = database
        self.gmail_generator = GmailGenerator(database['gmail'])
        self.gcalendar_generator = GcalendarGenerator(database['gcalendar'])
        self.message_generator = MessageGenerator()
        self.generators = [self.gmail_generator, self.gcalendar_generator, self.message_generator]#, self.hotel_generator
        '''
        transfer probabolity matrix 
        [hotel attraction restaurant] to [do-not-trans hotel attraction restaurant]
        '''
        self.trans_matrix = [[0.3, 0.45, 0.45], [0.3, 0.3, 0.3], [0.3, 0.3, 0.3]]

    def generate(self, exist_goal):
        goal = []
        if exist_goal["領域"] == "Gmail":
            index = 0
        elif exist_goal["領域"] == "Calendar":
            index = 1
        else:
            index = 2

        trans_exist = [-1, -1, -1]
        exist_goal_required_info = exist_goal["需求訊息"]
        for item in exist_goal_required_info:
            if item[0] == "名稱":
                trans_exist[0] = 1
            if item[0] == "郵件主旨":
                trans_exist[1] = 1
            if item[0] == "收件者" or item[0] == "寄件者":
                trans_exist[2] = 1
        #print('exist_goal', exist_goal)
        #print(self.trans_matrix[index][0] * trans_exist[0])
        #print(self.trans_matrix[index][1] * trans_exist[1])
        mail = random.random()
        if mail < self.trans_matrix[index][0] * trans_exist[0]:
            goal.append(self.generators[0].generate(call_count(), exist_goal))
            #print("Gmail", mail, self.trans_matrix[index][0], trans_exist[0])

        calendar = random.random()
        if calendar < self.trans_matrix[index][1] * trans_exist[1]:
            goal.append(self.generators[1].generate(call_count(), exist_goal))
            #print("Calendar", calendar, self.trans_matrix[index][1], trans_exist[1])

        message = random.random()
        if message < self.trans_matrix[index][2] * trans_exist[2]:
            goal.append(self.generators[2].generate(call_count(), exist_goal))
            #print("Message", message, self.trans_matrix[index][2], trans_exist[2])
        
        return goal

def load_json(database_dir, filename):
    list_data = json.load(open(os.path.join(database_dir, filename), encoding='utf-8'))
    return {x[0]: x[1] for x in list_data}

def generate_method(database_dir, single_domain=False, cross_domain=False, multi_target=True):
    """
    single_domain: 单领域生成还是多领域单独生成
    cross_domain: 是否需要跨领域跳转
    multi_target: （单个领域内）是否多目标
    """
    database = {
        'gmail': load_json(database_dir, os.path.join(database_dir, 'gmail_db.json')),
        'gcalendar': load_json(database_dir, os.path.join(database_dir, 'gcalendar_db.json'))
        #'restaurant': load_json(database_dir, os.path.join(database_dir, 'restaurant_db.json')),
    }
    global goal_num
    goal_num = 0

    # 单领域单目标
    if single_domain and not multi_target:
        # print('method-单领域单目标生成')
        domain_index = random.randint(1, 3)
        single_domain_generator = SingleDomainGenerator(database, domain_index=domain_index)
        single_domain_goal = single_domain_generator.generate(multi_target=False)
        return single_domain_goal
    # 多领域单独生成
    elif not single_domain and not cross_domain and not multi_target:
        # print('method-多领域单独生成')
        single_domain_generator = SingleDomainGenerator(database)
        single_domain_goals = single_domain_generator.generate(multi_target=False)
        # 确保总数至少有一个目标生成
        assert len(single_domain_goals) > 0

        goal_list = single_domain_goals
        return goal_list
    # 多领域可跨领域生成
    elif not single_domain and cross_domain and not multi_target:
        print('method-多领域可跨领域生成')
        # 首先进行单领域单独生成
        single_domain_generator = SingleDomainGenerator(database)
        single_domain_goals = single_domain_generator.generate(multi_target=False)
        
        # # 进行跨领域生成（跳转）
        cross_domain_generator = CrossDomainGenerator(database)
        cross_domain_goals = []
        copy_single_domain_goals = deepcopy(single_domain_goals)
        random.shuffle(copy_single_domain_goals)
        
        for goal in copy_single_domain_goals:
            #print(goal)
            if len(single_domain_goals) + len(cross_domain_goals) == goal_max:
                break
            for cross_goal in cross_domain_generator.generate(goal):
                #print(cross_goal)
                if len(single_domain_goals) + len(cross_domain_goals) == goal_max:
                    break
                cross_domain_goals.append(cross_goal)

        goal_list = single_domain_goals + cross_domain_goals
        return goal_list
    # 多领域多目标单独生成
    elif not single_domain and not cross_domain and multi_target:
        # print('method-多领域多目标单独生成')
        single_domain_generator = SingleDomainGenerator(database)
        single_domain_goals = single_domain_generator.generate(multi_target=True)

        goal_list = single_domain_goals
        return goal_list
    # 多领域多目标可跨领域生成
    elif not single_domain and cross_domain and multi_target:
        # print('method-多领域多目标可跨领域生成')
        # 首先进行单领域多目标独立生成
        single_domain_generator = SingleDomainGenerator(database)
        single_domain_goals = single_domain_generator.generate(multi_target=True)

        # 进行跨领域生成（跳转）
        cross_domain_generator = CrossDomainGenerator(database)
        cross_domain_goals = []
        copy_single_domain_goals = deepcopy(single_domain_goals)
        random.shuffle(copy_single_domain_goals)
        for goal in copy_single_domain_goals:
            if len(single_domain_goals) + len(cross_domain_goals) == goal_max:
                break
            for cross_goal in cross_domain_generator.generate(goal):
                if len(single_domain_goals) + len(cross_domain_goals) == goal_max:
                    break
                cross_domain_goals.append(cross_goal)

        goal_list = single_domain_goals + cross_domain_goals
        return goal_list

    else:
        raise LookupError('current method is not supported')
        return []

def generate_sentence(goal_list=[]):
    sentence_generator = SentenceGenerator()
    return sentence_generator.generate(goal_list)

if __name__ == "__main__":
    pprint(GoalGenerator.generate())