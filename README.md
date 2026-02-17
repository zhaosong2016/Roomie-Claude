# Roomie 拼房小程序 - 使用说明

## 运行方法

### 1. 安装依赖
```bash
pip install streamlit
```

### 2. 启动程序
在终端中进入项目文件夹，运行：
```bash
streamlit run app.py
```

程序会自动在浏览器中打开。

### 3. 停止程序
在终端按 `Ctrl + C`

## 数据文件

程序会自动创建 `room_data.json` 文件来存储用户数据。

## 部署到服务器

如果要部署到你的腾讯云服务器：

1. 上传 `app.py` 到服务器
2. 安装 streamlit：`pip3 install streamlit`
3. 后台运行：`nohup streamlit run app.py --server.port 5000 &`
4. 访问：`http://你的服务器IP:5000`

## 字段说明

详见 `数据结构说明.md`
