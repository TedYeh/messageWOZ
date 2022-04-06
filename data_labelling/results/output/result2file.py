import json
data = {}
with open('4.json', 'r', encoding='utf-8') as json_file:
    results = json.loads(json_file.read())
    for res in results:
        for key, value in res.items():
            if key == 'task':
                data[value] = {}
                file_id = value
            elif key == 'user': data[file_id]["sys-usr"] = value
            elif key == "created_at": continue
            else:
                msg = list(value)     
                if 'message' not in data:data[file_id]['message'] = []  
                         
                for m in msg:
                    tmp_dict = {}
                    tmp_dict["content"] = m["content"]
                    tmp_dict["role"] = "usr" if m["role"]==1 else "sys"
                    tmp_dict["dialog_act"] = m['payload']["dialog_act"] if m["role"]==1 else m['payload'][0]["dialog_act"]
                    if m["role"]==1: tmp_dict["user_state"] = m['payload']["user_state"] 
                    else: 
                        sys_state = {}
                        for key, value in m['payload'][0]["query"].items():
                            sys_state[key] = value["params"] if value["checked"] else ""
                        tmp_dict["sys_state"] = {m['payload'][0]["field"]: sys_state}
                    data[file_id]['message'].append(tmp_dict)
    print(json.loads(json.dumps(data, indent = 5)))
with open('out.json', 'w') as f:json.dump(data, f, indent = 5)