import json
import os
import re

project_names = ["ActiveMQ", "Hadoop", "HDFS", "Hive", "MAPREDUCE", "Storm", "YARN", "Zookeeper"]


def get_log_text(bug_report):
    fields = bug_report.get('fields', {})
    summary = fields.get('summary', '')
    description = fields.get('description', '')

    # 确保 summary 和 description 为字符串
    summary = summary if isinstance(summary, str) else ''
    description = description if isinstance(description, str) else ''

    log_text = summary + '\n' + description

    log_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \w+ [\w\.]+: .+$'

    # 使用 re.finditer 提取所有匹配的日志行
    matches = re.finditer(log_pattern, log_text, re.MULTILINE)
    matched_logs = [match.group(0) for match in matches]

    if matched_logs:
        return '\n'.join(matched_logs)
    else:
        return None


if __name__ == '__main__':
    '''
        处理bug_report并获取该报告的日志信息
    '''
    for project_name in project_names:
        directory = os.path.join('../ProcessData/bug_reports', project_name, 'details')

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
            json_file_path = os.path.join('../ProcessData/bug_reports', project_name, f'{name}.json')
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
                output_dir = os.path.join('../ProcessData/bug_reports', project_name)
                os.makedirs(output_dir, exist_ok=True)

                # 定义输出文件路径
                output_file_path = os.path.join(output_dir, f'{name}_logtext.txt')

                try:
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(log_text)
                    print(f"日志行已写入: {output_file_path}")
                except IOError as e:
                    print(f"无法写入文件 {output_file_path}: {e}")
