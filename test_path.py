import json
import os
import re

callgraph_path = f"../ProcessData/call_graph/Zookeeper/ZookeeperCallGraph.json"

# 检查文件是否存在
if not os.path.exists(callgraph_path):
    print(f"文件路径不存在：{callgraph_path}")
else:
    try:
        with open(callgraph_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            call_graph_json = json.loads(file_content)
    except json.JSONDecodeError as e:
        print(f"JSON 解码错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")