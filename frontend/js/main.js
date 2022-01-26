let current_role = 'USER';
let user_name = 'user';
let dialogue_id = 'Dialogue_0001.json';
let current_chat_list = {"dialogue_id": dialogue_id, "services": ["test"], "turns": []};
let current_chat_turn = 0;
const backend_url = 'http://localhost:8000';

// String format function
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

// Print message at chatbox
function print_message() {
    const chat_content = document.getElementById('chat_content');
    chat_content.innerHTML = '';
    current_chat_list["turns"].forEach(function (item) {
        let message = String.format('<br>({0}) {1}: {2}', item['turn_id'], item["speaker"], item["utterance"]);
        chat_content.innerHTML += message;
    });
}

// Send message to chatroom
function send_message() {
    const chat_content = document.getElementById('chat_input').value;
    // TODO: turn-frames
    let turn = {
        "speaker": current_role,
        "turn_id": current_chat_turn.toString(),
        "utterance": chat_content
    };
    current_chat_list["turns"].push(turn);
    print_message();
    // Log dialogue json data
    console.log(JSON.stringify(current_chat_list));
    // Clear the input
    document.getElementById('chat_input').value = '';
    // Switch role
    current_role = current_role === 'USER' ? 'SYSTEM' : 'USER';
    current_chat_turn += 1;
}

// Post data to backend
function post_data(url, data) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            console.log(xhr.responseText);
        }
    };

    xhr.send(data);
}

// Post
function post_json() {
    const post_url = backend_url + '/items'
    let data = `{
      "name": "myName",
      "description": "my text",
      "price": 12,
      "tax": 34.5
    }`;
    post_data(post_url, data);
}

// Post
function post_dialogue_data() {
    const post_url = backend_url + '/dialogue'
    post_data(post_url, JSON.stringify(current_chat_list));
}
