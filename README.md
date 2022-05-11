# 多領域任務導向用戶語音助理對話收集系統

## Environment setup

### Requirements
* python >= 3.6

### Development Startup

Before clone this repo, you need to install Redis on PC(Linux-Ubuntu)
```bash
# download redis package
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update

# the redis will running when it is installed successfully
sudo apt-get install redis
```


Run the following command and visit http://0.0.0.0:5000 (boardcast).

```bash
# clone the repo in branch GCPlogin
git clone -b GCPlogin --single-branch https://github.com/TedYeh/messageWOZ.git

# change the directory 
cd messageWOZ

# install dependencies
python3 -m pip install -r requirements.txt

# initialize the database
python3 resetdb.py

# start the server
python3 run.py
```
Or you can change the code 
```python
socket_io.run(app, host='0.0.0.0', port=5000)
```
to
```python
socket_io.run(app, host='127.0.0.1', port=5000)
```
in `data_labeling/__init__.py` to run the system in your localhost.

## 操作指南

### Login
運行系統後，會進入到登入畫面



<img src="img/login.png" alt="login" style="width:50%;"/>


### Register

若要使用普通用戶登入，點選`沒有帳號？點此註冊`來註冊帳號。

邀請碼為 `959592`，可以修改 `data_labelling/app.py` 的 `invitation_code`。

<img src="img/register.png" alt="register" style="width:50%;"/>

### Match
使用普通用戶才可進入對話匹配介面，進入介面後有**至少有一人選擇系統(助理)端，一人選擇用戶(使用者)端**，此时系統便會自動完成配對並進入對話介面。

提示：若在本地端 (http://localhost:5000) 測試此系統，可以使用 Chrome 的無痕視窗同時登入兩個帳號。

<img src="img/match.png" alt="drawing" style="width:70%;"/>



各對話頁面及設計請參考[標註系統操作說明]("MessageWOZ資料標註系統操作說明.pdf") `data_labeling/templates` 目錄下的`.html`。

管理员可以在后台导入预先定义的任务，导出对话数据。

导入任务的步骤是：在 Result Files 选项卡下，进入 inputs 目录，上传任务定义文件 tasks.json，再回到管理首页，点导入按钮。导入成功后，系统会告知导入成功的任务数量。此时也可以到 Task 选项卡查看详情。

导出数据直接在管理首页点下载全部即可。

### Admin

帳號名稱：root，密碼：root
