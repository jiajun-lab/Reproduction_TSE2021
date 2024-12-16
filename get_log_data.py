import re
import json
import os

def get_log_text(bug_report):
    fields = bug_report.get('fields', {})
    summary = fields.get('summary', '')
    description = fields.get('description', '')

    # 确保 description 为字符串，并去除换行符
    description = description if isinstance(description, str) else ''
    description = description.replace('\n', '\n').replace('\r', '\r')  # 去除换行符

    # 同样处理 summary 字段，去除换行符
    summary = summary.replace('\n', '\n').replace('\r', '\n')  # 去除换行符

    # 合并 summary 和 description
    log_text = summary + ' ' + description

    # 调试输出，确认清洗后的日志文本
    # print("清洗后的 log_text:", log_text)

    log_text = re.sub(r'\s+', ' ', log_text)
    # 修改后的日志信息的正则表达式，使用 \s+ 匹配多个空白字符
    log_pattern = r'\d{2}:\d{2}:\d{2},\d{3} \w+ .+'

    # 获取堆栈跟踪信息的正则表达式
    # stack_trace_pattern = r'at ([\w\.]+)\(([\w]+\.java):\d+\)'

    # 使用 re.findall 提取所有匹配的日志行
    matched_logs = re.findall(log_pattern, log_text, re.DOTALL)

    # 使用 re.finditer 提取堆栈跟踪信息
    # matched_stack = [match.group(0) for match in re.finditer(stack_trace_pattern, log_text)]

    # 调试输出，确认匹配结果
    if matched_logs:
        print("matched_logs:", matched_logs)
    # print("matched_stack:", matched_stack)

    # 合并所有匹配的日志行和堆栈跟踪信息
    s_logs = '\n'.join(matched_logs)
    # s_stack_trace = '\n'.join(matched_stack)
    # s_report = s_logs + '\n' + s_stack_trace
    #
    # if s_report.strip():
    #     return s_report
    # else:
    #     return None
    if s_logs.strip():
        return s_logs
    else:
        return None

if __name__ == '__main__':
    '''
        处理bug_report并获取该报告的日志信息
    '''
    project_names = ["ActiveMQ", "Hadoop", "HDFS", "Hive", "MAPREDUCE", "Storm", "YARN", "Zookeeper"]
    for project_name in project_names:
        directory = os.path.join('../pathidea/ProcessData/bug_reports', project_name)

        # 检查目录是否存在
        if not os.path.isdir(directory):
            print(f"目录不存在: {directory}")
            continue

        try:
            items = os.listdir(directory)
        except OSError as e:
            print(f"无法访问目录 {directory}: {e}")
            continue

        # 仅获取文件，忽略文件夹，并去除扩展名
        files = [os.path.splitext(item)[0] for item in items if os.path.isfile(os.path.join(directory, item)) and item.endswith('.json')]
        print(f"正在处理项目 '{project_name}' 的文件: {files}")

        for name in files:
            json_file_path = os.path.join('../pathidea/ProcessData/bug_reports', project_name, f'{name}.json')
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"无法读取或解析文件 {json_file_path}: {e}")
                continue

            # 判断是否含有符合条件的日志信息
            log_text = get_log_text(data)
            if log_text:
                # 确保输出目录存在
                output_dir = os.path.join('../pathidea/ProcessData/log_texts', project_name)
                os.makedirs(output_dir, exist_ok=True)

                # 定义输出文件路径
                output_file_path = os.path.join(output_dir, f'{name}_log_text.txt')

                try:
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(log_text)
                    print(f"日志行已写入: {output_file_path}")
                except IOError as e:
                    print(f"无法写入文件 {output_file_path}: {e}")
