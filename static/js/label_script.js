let file_list = [];
const backend_url = 'http://localhost:8000';

function load_file_list() {
    fetch(backend_url + '/file', {})
        .then((response) => {
            return response.json();
        }).then((jsonData) => {
        file_list = jsonData;
        load_dropdown_list('dialogue-file-list', 'File', file_list);
    }).catch((err) => {
        console.log('Error:', err);
    });
}

function dropdown_file_list_onchange() {
    const file_list_dropdown = document.getElementById('dialogue-file-list');
    const file_path = file_list_dropdown.options[file_list_dropdown.selectedIndex].value;
    // let gettext = file_list_dropdown.options[file_list_dropdown.selectedIndex].text;

    fetch(backend_url + '/dialogue_id_list', {
        method: 'POST',
        // headers 加入 json 格式
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        // body 將 json 轉字串送出
        body: JSON.stringify({
            'file': file_path
        })
    }).then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response.statusText);
        }
    }).then((jsonData) => {
        load_dropdown_list('dialogue-id-list', 'Dialogue ID', jsonData);
        //console.log(jsonData);
    }).catch((err) => {
        console.log(err);
    })
}

function load_dropdown_list(element_id, empty_option_text, item_list) {
    let tree = document.createDocumentFragment();
    let empty_option = document.createElement('option');
    empty_option.setAttribute('selected', '');
    empty_option.innerText = empty_option_text;
    tree.appendChild(empty_option);

    item_list.forEach(function (item) {
        let option = document.createElement('option');
        option.setAttribute('value', item);
        option.innerText = item;
        tree.appendChild(option);
    });

    const list_dropdown = document.getElementById(element_id);
    list_dropdown.innerHTML = '';
    list_dropdown.appendChild(tree);
}


// 清空聊天室
function reset_chat_table() {
    //TODO: reset dialogue data
    //reset_dialogue_data();
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

function load_dialogue_content() {
    const file_list_dropdown = document.getElementById('dialogue-file-list');
    const file_path = file_list_dropdown.options[file_list_dropdown.selectedIndex].value;
    const dialogue_id_list_dropdown = document.getElementById('dialogue-id-list');
    const dialogue_id = dialogue_id_list_dropdown.options[dialogue_id_list_dropdown.selectedIndex].value;

    fetch(backend_url + '/dialogue_content', {
        method: 'POST',
        // headers 加入 json 格式
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        // body 將 json 轉字串送出
        body: JSON.stringify({
            'file': file_path,
            'dialogue_id': dialogue_id
        })
    }).then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response.statusText);
        }
    }).then((jsonData) => {
        reset_chat_table();
        jsonData['turns'].forEach(function (turn) {
            add_chat_row(turn['turn_id'], turn['speaker'], turn['utterance'])
        });
        console.log(jsonData);
    }).catch((err) => {
        console.log(err);
    })
}
