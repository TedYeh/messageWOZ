let current_speaker = 'USER';
let user_name = 'user';
let dialogue_file_name = 'dialogue_0001';
let current_dialogue = {'dialogue_id': '', 'services': [], 'turns': []};
let current_dialogue_turn = 0;
let current_schema = {};
const backend_url = 'http://localhost:8000';

// String Format
if (!String.format) {
    String.format = function (format) {
        let args = Array.prototype.slice.call(arguments, 1);
        return format.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}

// 重置 Dialogue 資料
function reset_dialogue_data() {
    current_speaker = 'USER';
    current_dialogue = {'dialogue_id': '', 'services': [], 'turns': []};
    current_dialogue_turn = 0;
}

// 傳送訊息至聊天室
function send_message() {
    // 取得訊息內容，若為空值則退出
    const dialogue_content = document.getElementById('chat_input').value.trim();
    if (dialogue_content === '') {
        return;
    }

    // 將訊息放到 current_dialogue 內
    let turn = {
        'speaker': current_speaker,
        'turn_id': current_dialogue_turn.toString(),
        'utterance': dialogue_content
    };
    current_dialogue['turns'].push(turn);

    // 輸出訊息到頁面
    add_chat_row(current_dialogue_turn, current_speaker, dialogue_content);
    // Log dialogue json data
    // console.log(JSON.stringify(current_dialogue));
    // 將訊息框清空
    document.getElementById('chat_input').value = '';
    // 切換對話角色 (USER <--> SYSTEM)
    current_speaker = current_speaker === 'USER' ? 'SYSTEM' : 'USER';
    current_dialogue_turn += 1;
}

// 確認是否上傳對話內容，確定後上傳
function submit_dialogue() {
    user_name = document.getElementById('user-name').value.trim();
    Swal.fire({
        title: '你確定嗎？',
        text: '按下確定後，資料就會上傳至伺服器！',
        showDenyButton: true,
        confirmButtonText: '確定',
        denyButtonText: '取消',
        icon: 'warning'
    }).then((result) => {
        // 如果按下確定
        if (result.isConfirmed) {
            get_user_state_data();
            post_dialogue_data();
        }
    })
}

// 上傳資料對話內容
function post_dialogue_data() {
    fetch(backend_url + '/upload_dialogue', {
        method: 'POST',
        // headers 加入 json 格式
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        // body 將 json 轉字串送出
        body: JSON.stringify({
            'dialogue': current_dialogue,
            'user': user_name,
            'filename': dialogue_file_name
        })
    }).then((response) => {
        // 如果上傳成功，則清空 user state 和聊天室
        if (response.ok) {
            Swal.fire('上傳成功', '', 'success');
            reset_user_state_table();
            reset_chat_table();
            return response.json();
        } else {
            throw new Error(response.statusText);
        }
    }).then((jsonData) => {
        console.log(jsonData);
    }).catch((err) => {
        console.log(err);
        Swal.fire('發生錯誤', err.toString(), 'error');
    })
}

// 獲得新的 Initial User State
function get_user_state() {
    fetch(backend_url + '/schema', {})
        .then((response) => {
            return response.json();
        }).then((jsonData) => {
        current_schema = jsonData;
        console.log(jsonData);

        let i = 0;
        reset_user_state_table();
        current_schema['slots'].forEach(function (item) {
            item.forEach(function (new_slot) {
                add_user_state_row(i, new_slot['name'], new_slot['possible_values'][0], new_slot['chinese_description']);
            });
            i += 2;
        });
        current_dialogue['services'] = [current_schema['service_name']]

    }).catch((err) => {
        console.log('Error:', err);
    });
}

// 清空 User State 表格
function reset_user_state_table() {
    document.getElementById('initial-user-state').innerHTML = '';

    let tree = document.createDocumentFragment();
    let table = document.createElement('table');
    table.setAttribute('id', 'user-state-table');
    table.setAttribute('class', 'table');
    let thead = document.createElement('thead');
    let tbody = document.createElement('tbody');
    let tr = document.createElement('tr');
    const title_list = ['#', 'Slot', 'Value', 'Description'];
    title_list.forEach(function (item) {
        let th = document.createElement('th');
        th.setAttribute('scope', 'col');
        th.innerHTML = item;
        tr.appendChild(th);
    });
    thead.appendChild(tr);
    table.appendChild(thead);
    table.appendChild(tbody);
    tree.appendChild(table);

    document.getElementById('initial-user-state').appendChild(tree);
}

// 在 User State 表格新增一列 Slot
function add_user_state_row(slot_num, slot_name, slot_value, slot_description) {
    let tbody = document.getElementById('user-state-table').getElementsByTagName('tbody')[0];
    let tree = document.createDocumentFragment();
    let tr = document.createElement('tr');

    let th = document.createElement('th');
    th.setAttribute('scope', 'row');
    th.setAttribute('id', 'turn-' + slot_name);
    th.innerHTML = slot_num;
    tr.appendChild(th);

    let td = document.createElement('td');
    td.innerHTML = slot_name;
    tr.appendChild(td);

    td = document.createElement('td');
    let slot_value_input = document.createElement('input');
    slot_value_input.setAttribute('id', 'input-' + slot_name);
    if (slot_value !== undefined) {
        slot_value_input.setAttribute('value', slot_value);
        slot_value_input.disabled = true;
    }
    td.appendChild(slot_value_input);
    tr.appendChild(td);

    td = document.createElement('td');
    td.innerHTML = slot_description;
    tr.appendChild(td);

    tree.appendChild(tr);
    tbody.appendChild(tree);
}

// 清空聊天室
function reset_chat_table() {
    reset_dialogue_data();
    document.getElementById('chat_content').innerHTML = '';

    let tree = document.createDocumentFragment();
    let table = document.createElement('table');
    table.setAttribute('id', 'chat-table');
    table.setAttribute('class', 'table');
    let thead = document.createElement('thead');
    let tbody = document.createElement('tbody');
    let tr = document.createElement('tr');
    const title_list = ['#', 'Role', 'Message'];
    title_list.forEach(function (item) {
        let th = document.createElement('th');
        th.setAttribute('scope', 'col');
        th.innerHTML = item;
        tr.appendChild(th);
    });
    thead.appendChild(tr);
    table.appendChild(thead);
    table.appendChild(tbody);
    tree.appendChild(table);

    document.getElementById('chat_content').appendChild(tree);
}

// 在聊天室新增一列訊息
function add_chat_row(chat_num, chat_role, chat_message) {
    let tbody = document.getElementById('chat-table').getElementsByTagName('tbody')[0];
    let tree = document.createDocumentFragment();
    let tr = document.createElement('tr');

    let th = document.createElement('th');
    th.setAttribute('scope', 'row');
    th.innerHTML = chat_num;
    tr.appendChild(th);

    let td = document.createElement('td');
    td.innerHTML = chat_role;
    tr.appendChild(td);

    td = document.createElement('td');
    td.innerHTML = chat_message;
    tr.appendChild(td);

    tree.appendChild(tr);
    tbody.appendChild(tree);
}

// 整理 Dialogue 資料
function get_user_state_data() {
    // 彙整 User State 表格資料
    let user_state = {}
    current_schema['slots'].forEach(function (item) {
        item.forEach(function (current_slot) {
            const slot_turn_id = parseInt(document.getElementById('turn-' + current_slot['name']).innerText, 10);
            user_state[slot_turn_id] = {};
            user_state[slot_turn_id][current_slot['name']] = [document.getElementById('input-' + current_slot['name']).value.trim()];
        });
    });

    // 依序走訪 dialogue，把彙整好的 User State 填進去
    let i = 0;
    let state = {};
    state['active_intent'] = '';
    state['requested_slots'] = [];
    state['slot_values'] = {};

    current_dialogue['turns'].forEach(function (turn) {
        // 確定 current_dialogue 目前取出的 turn，是否為預期的順序
        let dialogue_turn_id = parseInt(turn['turn_id'], 10);
        if (dialogue_turn_id !== i) {
            throw new Error('turn_id and i doesn\'t match :' + dialogue_turn_id + '!==' + i);
        }

        state['slot_values'] = Object.assign({}, state['slot_values'], user_state[dialogue_turn_id]);

        if (dialogue_turn_id % 2 === 0) {  // USER
            let frame = {};
            frame['actions'] = [];
            frame['service'] = current_dialogue['services'][0];
            frame['slots'] = [];
            frame['state'] = state;

            turn['frames'] = [JSON.parse(JSON.stringify(frame))];
        } else {  // SYSTEM
            turn['frames'] = [];
        }

        i++;
    });

    console.log(current_dialogue);
}