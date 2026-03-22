import json
import networkx as nx

with open("/root/Roomie-Claude/room_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

target_names = {
    "张红艳","罗亚兰","孙陈","贾亦凡","张浩","苏贵民","车蓓蓓","张钊","李怡","符慧欣",
    "张飞","郭鹏飞","廖慧珍","黄小军","田立","刘星","胡萍","邓明娟","陈振桥","张平",
    "梅争春","罗建明","黄云开","杨华伟","方琦"
}

people = [u for u in data["users"] if u.get("group_code") == "YXSZ0410" and u["name"] in target_names]

def noise_ok(a, b):
    if a["noise_in"] == "weak" and b["noise_out"] != "silent": return False
    if b["noise_in"] == "weak" and a["noise_out"] != "silent": return False
    if a["noise_in"] == "medium" and b["noise_out"] == "bass": return False
    if b["noise_in"] == "medium" and a["noise_out"] == "bass": return False
    if a["noise_out"] == "bass" and b["noise_in"] != "strong": return False
    if b["noise_out"] == "bass" and a["noise_in"] != "strong": return False
    return True

def compatible(a, b):
    # 忽略日期，官方只管 4/9-4/10 两晚
    return (a["gender"] == b["gender"] and
            a["smoking"] == b["smoking"] and
            a["schedule"] == b["schedule"] and
            noise_ok(a, b))

G = nx.Graph()
G.add_nodes_from(range(len(people)))
for i in range(len(people)):
    for j in range(i+1, len(people)):
        if compatible(people[i], people[j]):
            G.add_edge(i, j)

matching = nx.max_weight_matching(G, maxcardinality=True)

matched = set()
result = []
for i, j in matching:
    a, b = people[i], people[j]
    result.append((a, b))
    matched.add(a["name"])
    matched.add(b["name"])

print("最大配对数：" + str(len(result)))
print()
for a, b in result:
    print("  " + a["name"] + " <-> " + b["name"] +
          "  [" + a["schedule"] + ", noise_in=" + a["noise_in"] + "/out=" + a["noise_out"] +
          " | noise_in=" + b["noise_in"] + "/out=" + b["noise_out"] + "]")

unmatched = [p["name"] for p in people if p["name"] not in matched]
print()
print("未匹配（" + str(len(unmatched)) + " 人）：" + ", ".join(unmatched))
