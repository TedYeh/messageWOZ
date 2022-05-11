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
import numpy as np

domains = ['活動', '郵件', '訊息']
actions = ['search', 'create']
slots = {'活動':['名稱', '時間', '參加者', '內容', '地點'], '郵件':['收件者', '寄件者', '主旨', '內容'], '訊息':['收件者', '內容']} 
domain_types = ['單領域', '多領域']
goal_num = 0
goal_max = 5
id = 0
# 你要{action[0]}一個{domain}。你想知道這個{domain}的{slot}
# other = '郵件' if domain == '活動' else '郵件'
# 你要{action[0]}一個{domain}。你希望{slot['活動'][2]||slot[domain][0]}有出現在id = {id}裡的{slot[other][2]||slot[other][0]}
# 你要{action[1]}一個{domain}給{}。

class GoalGenerator:
    @staticmethod
    def generate():
        goal_list = generate_method(
            database_dir=os.path.abspath(os.path.join(os.path.abspath(__file__),'../../../../data/crosswoz/database/')),
            single_domain=False, cross_domain=True,
            multi_target=False, transportation=True)
        goal_list = goals_reorder(goal_list)

        semantic_tuples = []
        for sub_goal in goal_list:
            sub_goal_id = sub_goal['id']
            domain = sub_goal['领域']
            for slot, value in sub_goal['约束条件']:
                semantic_tuples.append([sub_goal_id, domain, slot, value, False])
            for slot, value in sub_goal['需求信息']:
                if '周边' in slot or slot=='推荐菜':
                    value = []
                semantic_tuples.append([sub_goal_id, domain, slot, value, False])
        return semantic_tuples


def call_count():
    global goal_num
    goal_num += 1
    return goal_num


class SingleDomainGenerator():
    def __init__(self, database, domain_index=None):
        self.database = database
        self.attraction_generator = AttractionGenerator(database['attraction'])
        self.restaurant_generator = RestaurantGenerator(database['restaurant'])
        self.hotel_generator = HotelGenerator(database['hotel'])
        self.generators = [self.attraction_generator, self.restaurant_generator, self.hotel_generator]
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
                if random.random() < 0.8:
                    goal.append(generator.generate(call_count()))
                    # 多领域多目标生成，控制总数不超过5
                    if len(goal) == goal_max:
                        break
                    if multi_target and random.random() < 0.2:
                        goal.append(generator.generate(call_count()))

            if len(goal) == 0:
                goal.append(self.generators[0].generate(call_count()))
        assert 0 < len(goal) <= goal_max
        return goal


class CrossDomainGenerator():
    def __init__(self, database):
        self.database = database
        self.attraction_generator = AttractionGenerator(database['attraction'])
        self.restaurant_generator = RestaurantGenerator(database['restaurant'])
        self.hotel_generator = HotelGenerator(database['hotel'])
        self.generators = [self.hotel_generator, self.attraction_generator, self.restaurant_generator]
        '''
        transfer probabolity matrix 
        [hotel attraction restaurant] to [do-not-trans hotel attraction restaurant]
        '''
        self.trans_matrix = [[0, 0.45, 0.45], [0.3, 0.3, 0.3], [0.3, 0.3, 0.3]]

    def generate(self, exist_goal):
        goal = []
        if exist_goal["领域"] == "酒店":
            index = 0
        elif exist_goal["领域"] == "景点":
            index = 1
        else:
            index = 2

        trans_exist = [-1, -1, -1]
        exist_goal_required_info = exist_goal["需求信息"]
        for item in exist_goal_required_info:
            if item[0] == "周边酒店":
                trans_exist[0] = 1
            if item[0] == "周边景点":
                trans_exist[1] = 1
            if item[0] == "周边餐馆":
                trans_exist[2] = 1

        if random.random() < self.trans_matrix[index][0] * trans_exist[0]:
            goal.append(self.generators[0].generate(call_count(), exist_goal))
        if random.random() < self.trans_matrix[index][1] * trans_exist[1]:
            goal.append(self.generators[1].generate(call_count(), exist_goal))
        if random.random() < self.trans_matrix[index][2] * trans_exist[2]:
            goal.append(self.generators[2].generate(call_count(), exist_goal))
        return goal

def load_json(database_dir, filename):
    list_data = json.load(open(os.path.join(database_dir, filename), encoding='utf-8'))
    return {x[0]: x[1] for x in list_data}

def generate_method(database_dir, single_domain=False, cross_domain=False, multi_target=False, transportation=False):
    """
    single_domain: 单领域生成还是多领域单独生成
    cross_domain: 是否需要跨领域跳转
    multi_target: （单个领域内）是否多目标
    transportation: 是否进行出租、地铁生成
    """
    database = {
        'attraction': load_json(database_dir, os.path.join(database_dir, 'attraction_db.json')),
        'hotel': load_json(database_dir, os.path.join(database_dir, 'hotel_db.json')),
        'restaurant': load_json(database_dir, os.path.join(database_dir, 'restaurant_db.json')),
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
        # print('method-多领域可跨领域生成')
        # 首先进行单领域单独生成
        single_domain_generator = SingleDomainGenerator(database)
        single_domain_goals = single_domain_generator.generate(multi_target=False)

        # # 进行跨领域生成（跳转）
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

    # 异常处理
    else:
        raise LookupError('current method is not supported')
        return []

if __name__ == "__main__":
    