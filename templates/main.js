let current_speaker = 'USER';
let user_name = 'user';
let dialogue_file_name = 'dialogue_0001';
let current_dialogue = {'dialogue_id': '', 'services': [], 'turns': []};
let current_dialogue_turn = 0;
let current_schema = {};
const backend_url = 'http://localhost:8000';

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