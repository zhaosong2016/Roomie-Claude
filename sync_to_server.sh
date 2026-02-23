#!/bin/bash

# 同步修改的文件到服务器
# 2026-02-21: 同步 api.py 修改（增加 pending_count 统计）

echo "开始同步文件到服务器..."

# 同步 api.py
echo "1. 同步 api.py..."
scp api.py root@49.233.127.228:/root/Roomie-Claude/

echo "2. 重启 API 服务..."
ssh root@49.233.127.228 << 'EOF'
cd /root/Roomie-Claude
pkill -f "python.*api.py"
nohup python3 api.py > api.log 2>&1 &
sleep 2
echo "API 服务已重启"
EOF

echo "3. 验证 API 服务..."
curl http://49.233.127.228:5000/api/health

echo ""
echo "同步完成！"
