import json
import re
import os
from collections import deque


project_names = ["ActiveMQ", "Hadoop", "HDFS", "Hive", "MAPREDUCE", "Storm", "YARN", "Zookeeper"]

def bfs_find_path(current_method, next_method, call_graph):
    """
    在调用图中查找从current_method到next_method的所有路径。
    使用BFS来实现。
    
    :param current_method: 当前日志方法
    :param next_method: 下一个方法
    :param call_graph: 调用图，字典格式，存储方法及其调用的其他方法
    :return: 所有从current_method到next_method的路径
    """
    # 队列，存储路径，每个元素是路径中的一部分（一个方法）
    queue = deque([[current_method]])
    # 存储已经访问过的方法，避免重复遍历
    visited = set([current_method])
    # 存储所有的路径
    paths = []

    # BFS 遍历
    while queue:
        # 取出当前路径
        current_path = queue.popleft()
        # 获取当前路径的最后一个方法
        last_method = current_path[-1]

        # 如果找到了目标方法，则记录路径
        if last_method == next_method:
            paths.append(current_path)
            continue

        # 遍历当前方法能调用的其他方法
        if last_method in call_graph:
            for called_method in call_graph[last_method]:
                # 只有未访问过的节点才能继续遍历
                if called_method not in visited:
                    visited.add(called_method)
                    # 将新的路径加入队列
                    queue.append(current_path + [called_method])

    return paths


def extract_methods_from_log(log_text):
    # 正则表达式匹配堆栈跟踪信息
    stack_pattern = r'\s*at (\S+\.\S+)\.(\S+)\((\S+):(\d+)\)'
    
    # 正则表达式匹配日志内容中的方法（假设方法格式为小写字母开头）
    log_method_pattern = r'(\w+\.\w+)\('

    methods = []

    # 遍历日志文本行
    for line in log_text.splitlines():
        # 查找堆栈信息中的方法
        stack_match = re.match(stack_pattern, line)
        if stack_match:
            # 提取方法名并添加到结果列表
            class_name, method_name, file, line_num = stack_match.groups()
            method_full_name = f"{class_name}.{method_name}"
            methods.append(process_method_name(method_full_name))
        
        # 查找日志内容中的方法
        log_method_matches = re.findall(log_method_pattern, line)
        for match in log_method_matches:
            methods.append(process_method_name(match))
    # return methods
    # 去重并保持顺序
    unique_methods = list(dict.fromkeys(methods))  
    return unique_methods

def process_method_name(method):
    parts = method.split(".")
    if len(parts) < 2:
        return method
    method = f"{parts[-2]}.{parts[-1]}"

    return method


# 加载调用图
def load_call_graph(callgraph_json):
    # 用于存储调用图的字典
    call_graph = {}

    # 遍历 JSON 数据
    for method, calls in callgraph_json.items():
        # 每个方法的值是一个列表，保存该方法调用的所有其他方法
        method = process_method_name(method)
        call_graph[method] = []

        # 解析方法调用链
        for call in calls:
            # 提取方法调用路径
            called_method = process_method_name(call.split(" -> ")[1])
            call_graph[method].append(called_method)
    
    return call_graph

# 重构执行路径
def reconstruct_execution_paths(log_methods, call_graph):
    execution_paths = []
    for i in range(len(log_methods) - 2):
        path = bfs_find_path(log_methods[i], log_methods[i+1], call_graph)
        if path:
            execution_paths.append(path)
    return execution_paths

# 去除重复路径
def remove_duplicate_paths(execution_paths):
    unique_paths = []
    seen_paths = set()
    for path in execution_paths:
        path_tuple = tuple(path)
        if path_tuple not in seen_paths:
            unique_paths.append(path)
            seen_paths.add(path_tuple)
    return unique_paths



# 计算路径分数（path_score）
def calculate_path_score(path, call_graph):
    score = 0


    return score

# 分析路径（包括重构路径和计算分数）
def analyze_paths(project_name, log_text, report_name):
    try:
        if log_text:
            # 获得日志中方法
            log_methods = extract_methods_from_log(log_text)
            callgraph_path = f"../ProcessData/call_graph/{project_name}/{project_name}CallGraph.json"

            with open(callgraph_path, 'r', encoding='utf-8') as file:
                call_graph_json = json.load(file)
                # 加载调用图
                call_graph = load_call_graph(call_graph_json)
            
            # 获取执行路径
            execution_paths = reconstruct_execution_paths(log_methods, call_graph)
            
            # 去除重复路径
            unique_paths = remove_duplicate_paths(execution_paths)
            
            # 计算路径得分
            path_scores = []
            for path in unique_paths:
                score = calculate_path_score(path, call_graph)
                path_scores.append((path, score))
            
            # 保存路径和得分到单独的文件
            output_directory = f"../ProcessData/path_results"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            
            output_file_path = f"{output_directory}/{report_name}_execution_paths_scored.txt"
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                for path, score in path_scores:
                    output_file.write(f"Score: {score} -> {' -> '.join([f'{cls}.{method}' for cls, method in path])}\n")
    except Exception as e:
        print(f"Error processing bug report {report_name}: {e}")

if __name__ == "__main__":
    # Example for analyzing paths for a specific project
    project_name = "YARN"
    
    directory = f'../ProcessData/log_texts/{project_name}'
    if not os.path.exists(directory):
        print(f"Directory for {project_name} not found.")
    else:
        files = [item for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item))]
        for name in files:
            try:
                with open(f"{directory}/{name}","r") as f:
                    log_text = f.read()
                # Analyze the execution paths and compute scores
                analyze_paths(project_name, log_text, name.replace("txt", ""))
            except Exception as e:
                print(f"Error processing file {name}: {e}")
