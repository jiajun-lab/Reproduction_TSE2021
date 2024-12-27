import json
import re
import os

import evaluation


project_names = ["ActiveMQ", "Hadoop", "HDFS", "Hive", "MAPREDUCE", "Storm", "YARN", "Zookeeper"]

def extract_methods_from_log(log_text):
    # 正则表达式匹配 'at ' 后的类和方法信息
    pattern = r'at\s+([A-Za-z0-9_.$]+\.[A-Za-z0-9_$]+)\('

    matches = re.findall(pattern, log_text)

    methods = [method_name for method_name in matches]

    # # 遍历日志文本行
    # for line in log_text.splitlines():
    #     # 查找堆栈信息中的方法
    #     stack_match = re.match(log_method_pattern, line)
    #     log_match = re.match(log_method_pattern, line)
    #     if stack_match:
    #         # 提取方法名并添加到结果列表
    #         class_name, method_name, file, line_num = stack_match.groups()
    #         method_full_name = f"{class_name}.{method_name}"
    #         methods.append(process_method_name(method_full_name))
    #
    #     if log_match:
    #         # 提取方法名并添加到结果列表
    #         class_name, method_name, file, line_num = stack_match.groups()
    #         method_full_name = f"{class_name}.{method_name}"
    #         methods.append(process_method_name(method_full_name))

    # return methods
    # 去重并保持顺序
    unique_methods = list(dict.fromkeys(methods))  
    return unique_methods

def process_method_name(method):
    method.replaceAll("$", ".")
    return method

def process_vsm_scores(vsm_result):
    vsm_process_result = {}
    for line in vsm_result:
        if line != "":
            temp = line.split(": ")
            # vsm_class_name = re.sub("\.java", "", temp[0].split("/")[-1])
            vsm_class_name = temp[0]
            vsm_score = float(temp[1])
            vsm_process_result[vsm_class_name]= vsm_score
    return vsm_process_result

# 加载调用图
def load_call_graph(callgraph_json):
    call_graph = {}

    # 遍历 JSON 中的键值对
    for method, called_methods in callgraph_json.items():
        call_graph[method] = called_methods
    
    return call_graph

# 重构执行路径
def reconstruct_execution_paths(log_methods, call_graph):
    def dfs(method, call_graph, visited):
        """
        深度优先搜索，递归构建执行路径。
        Args:
            method (str): 当前方法。
            call_graph (dict): 调用图。
            visited (set): 已访问方法集合，防止循环。
        Returns:
            dict: 以当前方法为根的执行路径。
        """
        method = re.sub(r"\(.*?\)", "", method)
        if method in visited:  # 防止循环调用
            return None
        visited.add(method)

        path = {method: []}  # 当前方法为根节点
        if method in call_graph:  # 如果该方法存在于调用图中
            for next_method in call_graph[method]:
                sub_path = dfs(next_method, call_graph, visited)  # 递归构建子路径
                if sub_path:
                    path[method].append(sub_path)  # 添加子路径
        return path

    execution_paths = {}
    visited = set()
    for method in log_methods:
        if method not in visited:
            path = dfs(method, call_graph, visited)
            if path:
                execution_paths.update(path)
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

def find_class_in_execution_paths(execution_paths, target_class):
    """
    在 execution_paths 中查找某个类是否出现过。

    Args:
        execution_paths (dict): 执行路径的树状结构。
        target_class (str): 需要查找的类名。

    Returns:
        bool: 如果找到目标类，返回 True；否则返回 False。
    """
    for method, sub_paths in execution_paths.items():
        # 检查当前方法是否包含目标类名
        if target_class in method:
            return True
        # 递归检查子路径
        for sub_path in sub_paths:
            if find_class_in_execution_paths(sub_path, target_class):
                return True
    return False

# 计算路径分数（path_score）
def calculate_path_score(execution_paths, vsm_result_key, vsm_result_value, beta=0.2):
    vsm_class_name = re.sub("\.java", "", vsm_result_key.split("/")[-1])
    vsm_score = float(vsm_result_value)
    # print(vsm_class_name)

    if find_class_in_execution_paths(execution_paths, vsm_class_name):
        path_score = beta * vsm_score
        return vsm_result_key + ": " + str(path_score)

    return None


# 分析路径（包括重构路径和计算分数）
def analyze_paths(project_name, log_text, vsm_result, report_name):
    try:
        if log_text:
            # 获得日志中方法
            log_methods = extract_methods_from_log(log_text)
            callgraph_path = f"../pathidea/ProcessData/call_graph/{project_name}/{project_name}CallGraph.json"

            with open(callgraph_path, 'r', encoding='utf-8') as file:
                call_graph_json = json.load(file)
                # 加载调用图
                call_graph = load_call_graph(call_graph_json)
            
            # 获取执行路径
            execution_paths = reconstruct_execution_paths(log_methods, call_graph)

            # 去除重复路径
            # unique_paths = remove_duplicate_paths(execution_paths)

            # 保存路径和得分到单独的文件
            output_directory = f"../pathidea/ProcessData/path_results"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            output_file_path = f"{output_directory}/{report_name}_paths_score.txt"
            # 计算路径得分
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                for k,v in vsm_result.items():
                    score = calculate_path_score(execution_paths, k, v, beta=0.2)
                    if score:
                        output_file.write(f"{score}\n")

    except Exception as e:
        print(f"Error processing bug report {report_name}: {e}")

if __name__ == "__main__":
    # Example for analyzing paths for a specific project
    # project_name = "Zookeeper"

    for project_name in project_names:
        log_directory = f'../pathidea/ProcessData/log_texts/{project_name}'
        vsm_directory = f'../pathidea/ProcessData/vsm_result'
        if not os.path.exists(log_directory):
            print(f"Directory for {project_name} not found.")
        else:
            files = [item for item in os.listdir(log_directory) if os.path.isfile(os.path.join(log_directory, item))]
            for name in files:
                try:
                    # 读取日志内容
                    with open(f"{log_directory}/{name}", "r") as f:
                        log_text = f.read()
                    # 读取vsm得分
                    vsm_name = name.split("_")[0]+"_token_vsm.txt"
                    with open(f"{vsm_directory}/{vsm_name}", "r") as f:
                        vsm_result = f.read().split("\n")
                    process_vsm_score = evaluation.normalize_vsm_scores(process_vsm_scores(vsm_result))
                    # Analyze the execution paths and compute scores
                    analyze_paths(project_name, log_text, process_vsm_score, name.replace("_report_text.txt", ""))
                    print(f"Success processing file {name}")
                except Exception as e:
                    print(f"Error processing file {name}: {e}")
