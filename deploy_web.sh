#!/bin/bash
echo "1. 上传文件..."
scp api.py root@49.233.127.228:/root/Roomie-Claude/
scp index.html root@49.233.127.228:/root/Roomie-Claude/

echo "2. 重启服务..."
ssh root@49.233.127.228 "pkill -f 'python.*api.py'; sleep 1; cd /root/Roomie-Claude && nohup python3 api.py > api.log 2>&1 &"

echo "3. 等待启动..."
sleep 3

echo "4. 验证..."
curl -s http://49.233.127.228:5000/api/health
echo ""
echo "完成！访问地址：http://49.233.127.228:5000"
