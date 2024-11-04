import json
import re
import os
from collections import defaultdict

def extract_log_snippets(bug_report_text):
    # 使用正则表达式提取日志片段
    log_snippet_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) ([\w\.]+): (.+)'
    log_snippets = re.findall(log_snippet_pattern, bug_report_text)
    return log_snippets

def extract_stack_traces(bug_report_text):
    # 使用正则表达式提取堆栈跟踪信息
    stack_trace_pattern = r'at ([\w\.]+)\(([\w]+\.java):\d+\)'
    stack_traces = re.findall(stack_trace_pattern, bug_report_text)
    return stack_traces

def calculate_log_snippet_score(log_snippets):
    # 为日志片段中的每个文件分配固定分数0.1，只计算一次
    log_score = defaultdict(float)
    for snippet in log_snippets:
        class_name = snippet[2]  # Fully qualified class name
        file_name = class_name.split('.')[-1] + '.java'  # Derive file name
        log_score[file_name] = 0.1  # 只计算一次，每个文件分配0.1的分数
    return log_score

def calculate_stack_trace_score(stack_traces):
    # 为堆栈跟踪中的文件分配递减分数
    stack_trace_score = defaultdict(float)
    rank_score_map = [1.0, 0.5, 0.33, 0.25, 0.2, 0.17, 0.14, 0.12, 0.11, 0.1]  # 前10名的分数

    # 反转堆栈跟踪列表，使得越靠后的文件先被处理
    reversed_stack_traces = stack_traces[::-1]
    current_rank = 0
    for trace in reversed_stack_traces:
        file_name = trace[1]  # 提取文件名
        if current_rank < len(rank_score_map):
            stack_trace_score[file_name] = rank_score_map[current_rank]
        else:
            stack_trace_score[file_name] = 0.1  # 超过前10名的文件分数为0.1
        current_rank += 1
    return stack_trace_score

def combine_scores(log_score, stack_trace_score):
    # 合并日志片段和堆栈跟踪分数
    combined_score = defaultdict(float)
    for file_name, score in log_score.items():
        combined_score[file_name] += score
    for file_name, score in stack_trace_score.items():
        combined_score[file_name] += score
    return combined_score

def analyze_bug_report(bug_report_text):
    # 提取日志片段和堆栈跟踪信息
    log_snippets = extract_log_snippets(bug_report_text)
    stack_traces = extract_stack_traces(bug_report_text)

    # 计算日志片段和堆栈跟踪的分数
    log_score = calculate_log_snippet_score(log_snippets)
    stack_trace_score = calculate_stack_trace_score(stack_traces)

    # 合并并输出分数
    combined_score = combine_scores(log_score, stack_trace_score)
    return combined_score


def get_log_text(bug_report):
    fields = bug_report.get('fields', {})
    summary = fields.get('summary', '')
    description = fields.get('description', '')

    # 确保 summary 和 description 为字符串
    summary = summary if isinstance(summary, str) else ''
    description = description if isinstance(description, str) else ''

    log_text = summary + ' ' + description

    # 检查 description 是否包含日志或堆栈跟踪的格式
    # log_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \[.*?\] (DEBUG|ERROR|INFO|WARN) .*'
    # stack_trace_pattern = r'(?:Exception|Error|at\s).*(\n\s*at .*)+'
    log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) ([\w\.]+): (.+)'
    stack_trace_pattern = r'at ([\w\.]+)\(([\w]+\.java):\d+\)'
    if re.search(log_pattern, description) or re.search(stack_trace_pattern, description, re.MULTILINE):
        return log_text


if __name__ == '__main__':
    '''
        处理bug_report并获取该报告的日志和堆栈跟踪信息
    '''
    directory = 'bug_reports/Zookeeper/details'

    items = os.listdir(directory)

    # 仅获取文件，忽略文件夹
    files = [item.replace('.json', '') for item in items if os.path.isfile(os.path.join(directory, item))]
    print(files)

    log_scores = []
    for name in files:
        with open('bug_reports/Zookeeper/' + name + '.json', 'r') as f:
            data = json.load(f)

        # 判断是否含有log或堆栈跟踪信息
        log_text = get_log_text(data)
        if log_text is not None:
            # 分析日志并输出结果
            result = analyze_bug_report(log_text)
            # print('bug_reports/Zookeeper/' + name + '.json'+"文件可疑性分数:")
            temp_score = []
            for file, score in result.items():
                # print(f"{file}: {score:.2f}")
                temp_score.append([file, score])
                # 按照得分从大到小排序
                sorted_temp_score = sorted(temp_score, key=lambda x: x[1], reverse=True)
            log_scores.append([name, sorted_temp_score])

    # sorted_log_scores = sorted(log_scores, key=lambda x: x[0], reverse=True)
    print(f"共处理了 {len(log_scores)} 个错误报告。")

    # 创建log_result目录（如果不存在）
    output_dir = 'log_result'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for item in log_scores:
        name, temp_score = item
        # 写入到log_result/{name}_log.txt
        output_file = os.path.join(output_dir, f"{name}_log.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for file_name, score in temp_score:
                f.write(f"{file_name}: {score:.2f}\n")
        print(f"已将结果写入文件：{output_file}")
