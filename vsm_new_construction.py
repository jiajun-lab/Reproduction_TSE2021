# import numpy as np
# import os
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
#
# SEGMENT_SIZE = 800  # 设置分段大小为800个token
#
# def get_bug_tokens(base_path):
#     # 存储每个错误报告的 tokens 列表
#     bug_reports_tokens = []
#     project_names = []
#     bug_report_names = []
#
#     # 获取所有项目的文件夹列表，排除隐藏文件和非目录
#     projects = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')]
#
#     # 按照项目名称排序，确保列表顺序一致
#     projects.sort()
#
#     for project in projects:
#         project_path = os.path.join(base_path, project)
#
#         # 获取项目文件夹下的所有文件，排除隐藏文件
#         files = [f for f in os.listdir(project_path) if not f.startswith('.')]
#
#         # 过滤出 .txt 文件（每个txt文件对应一个错误报告）
#         tokens_files = [f for f in files if f.endswith('.txt')]
#
#         # 按照文件名排序，确保顺序一致
#         tokens_files.sort()
#
#         for tokens_file in tokens_files:
#             tokens_file_path = os.path.join(project_path, tokens_file)
#
#             # 打开并读取 tokens 文件
#             with open(tokens_file_path, 'r', encoding='utf-8') as f:
#                 tokens = [line.strip() for line in f if line.strip()]
#                 if tokens:
#                     bug_reports_tokens.append(tokens)
#                     project_names.append(project)
#                     bug_report_names.append(tokens_file.replace('.txt', ''))
#
#     return bug_reports_tokens, project_names, bug_report_names
#
# def get_source_files(base_path, project_name):
#     # 获取项目下所有的tokens文件
#     project_dir = os.path.join(base_path, project_name)
#     source_files = [f for f in os.listdir(project_dir) if f.endswith('_tokens.txt') and not f.startswith('.')]
#     source_files.sort()
#     return source_files
#
# def get_source_tokens(file_path):
#     # 读取源代码文件的tokens，并返回其相对路径和tokens
#     with open(file_path, 'r', encoding='utf-8') as f:
#         lines = f.readlines()
#         relative_path = lines[0].strip()  # 第一行是Java文件的相对路径
#         tokens = [line.strip() for line in lines[1:] if line.strip()]  # 剩余行是tokens
#     return relative_path, tokens
#
# def save_vsm_result(bug_report_name, vsm_results):
#     # 创建vsm_result文件夹（如果不存在）
#     output_dir = 'vsm_result'
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#
#     # 定义输出文件路径
#     output_file = os.path.join(output_dir, f"{bug_report_name}_vsm.txt")
#
#     # 将VSM结果写入txt文件，并按相似度排序
#     with open(output_file, 'w', encoding='utf-8') as f:
#         for result in vsm_results:
#             f.write(f"{result[0]}: {result[1]:.4f}\n")
#
# if __name__ == '__main__':
#
#     # 获取错误报告的 tokens 及对应项目名称和错误报告名称
#     bug_reports_tokens, project_names, bug_report_names = get_bug_tokens("bug_reports_tokens")
#
#     # 创建 TfidfVectorizer，移除编程语言关键字等停用词
#     stop_words = ['public', 'class', 'void', 'new', 'if', 'else', 'for', 'while', 'return', '{', '}', '(', ')', ';', '...']
#     vectorizer = TfidfVectorizer(stop_words=stop_words)
#
#     # 遍历每个错误报告及其对应的项目
#     for i, (bug_tokens, project_name, bug_report_name) in enumerate(zip(bug_reports_tokens, project_names, bug_report_names)):
#         # 将错误报告的 tokens 转换为字符串
#         bug_report_text = ' '.join(bug_tokens)
#
#         # 获取对应项目下的所有源代码tokens文件
#         source_files = get_source_files("source_code_tokens", project_name)
#
#         if not source_files:
#             print(f"未找到项目 {project_name} 的源代码tokens文件")
#             continue
#
#         vsm_results = []  # 存储相似度结果
#
#         # 遍历项目下的每个源代码tokens文件
#         for source_file in source_files:
#             source_file_path = os.path.join("source_code_tokens", project_name, source_file)
#             relative_path, source_tokens = get_source_tokens(source_file_path)
#
#             # 将源代码的 tokens 转换为字符串
#             source_code_text = ' '.join(source_tokens)
#
#             # 构建文档集合：一个错误报告 + 一个源代码段
#             documents = [bug_report_text, source_code_text]
#
#             # 计算 TF-IDF 矩阵
#             tfidf_matrix = vectorizer.fit_transform(documents)
#
#             # 分割错误报告和源代码段的向量
#             bug_report_vector = tfidf_matrix[0]  # 错误报告的向量
#             source_code_vector = tfidf_matrix[1]  # 源代码段的向量
#
#             # 计算相似度
#             similarity = cosine_similarity(bug_report_vector, source_code_vector.reshape(1, -1)).flatten()[0]
#
#             # 将相似度结果添加到vsm_results列表
#             vsm_results.append((relative_path, similarity))
#
#         # 按相似度从高到低排序
#         vsm_results.sort(key=lambda x: x[1], reverse=True)
#
#         # 保存结果到vsm_result文件夹中的对应错误报告txt文件
#         save_vsm_result(bug_report_name, vsm_results)
#
#         # 输出结果
#         print(f"错误报告 {i} ({bug_report_name}) 的相似度分析已完成，并保存到 vsm_result/{bug_report_name}_vsm.txt")

import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from multiprocessing import Pool

SEGMENT_SIZE = 800  # 设置分段大小为800个token

def get_bug_tokens(base_path):
    # 存储每个错误报告的 tokens 列表
    bug_reports_tokens = []
    project_names = []
    bug_report_names = []

    # 获取所有项目的文件夹列表，排除隐藏文件和非目录
    projects = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')]

    # 按照项目名称排序，确保列表顺序一致
    projects.sort()

    for project in projects:
        if project != 'ActiveMQ':
            project_path = os.path.join(base_path, project)

            # 获取项目文件夹下的所有文件，排除隐藏文件
            files = [f for f in os.listdir(project_path) if not f.startswith('.')]

            # 过滤出 .txt 文件（每个txt文件对应一个错误报告）
            tokens_files = [f for f in files if f.endswith('.txt')]

            # 按照文件名排序，确保顺序一致
            tokens_files.sort()

            for tokens_file in tokens_files:
                tokens_file_path = os.path.join(project_path, tokens_file)

                # 打开并读取 tokens 文件
                with open(tokens_file_path, 'r', encoding='utf-8') as f:
                    tokens = [line.strip() for line in f if line.strip()]
                    if tokens:
                        bug_reports_tokens.append(tokens)
                        project_names.append(project)
                        bug_report_names.append(tokens_file.replace('.txt', ''))

    return bug_reports_tokens, project_names, bug_report_names

def get_source_files(base_path, project_name):
    # 获取项目下所有的tokens文件
    project_dir = os.path.join(base_path, project_name)
    source_files = [f for f in os.listdir(project_dir) if f.endswith('_tokens.txt') and not f.startswith('.')]
    source_files.sort()
    return source_files

def get_source_tokens(file_path):
    # 读取源代码文件的tokens，并返回其相对路径和tokens
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        relative_path = lines[0].strip()  # 第一行是Java文件的相对路径
        tokens = [line.strip() for line in lines[1:] if line.strip()]  # 剩余行是tokens
    return relative_path, tokens

def save_vsm_result(bug_report_name, vsm_results):
    # 创建vsm_result文件夹（如果不存在）
    output_dir = 'vsm_result'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 定义输出文件路径
    output_file = os.path.join(output_dir, f"{bug_report_name}_vsm.txt")

    # 将VSM结果写入txt文件，并按相似度排序
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in vsm_results:
            f.write(f"{result[0]}: {result[1]:.4f}\n")

def process_source_file(args):
    bug_report_text, source_file_path, stop_words = args
    relative_path, source_tokens = get_source_tokens(source_file_path)

    # 将源代码的 tokens 转换为字符串
    source_code_text = ' '.join(source_tokens)

    # 构建文档集合：一个错误报告 + 一个源代码段
    documents = [bug_report_text, source_code_text]

    # 创建 TfidfVectorizer 实例
    vectorizer = TfidfVectorizer(stop_words=stop_words)

    # 计算 TF-IDF 矩阵
    tfidf_matrix = vectorizer.fit_transform(documents)

    # 分割错误报告和源代码段的向量
    bug_report_vector = tfidf_matrix[0]
    source_code_vector = tfidf_matrix[1]

    # 计算相似度
    similarity = cosine_similarity(bug_report_vector, source_code_vector.reshape(1, -1)).flatten()[0]

    return (relative_path, similarity)

if __name__ == '__main__':

    # 获取错误报告的 tokens 及对应项目名称和错误报告名称
    bug_reports_tokens, project_names, bug_report_names = get_bug_tokens("bug_reports_tokens")

    print(project_names)
    # 定义停用词列表
    stop_words = ['public', 'class', 'void', 'new', 'if', 'else', 'for', 'while', 'return',
                  '{', '}', '(', ')', ';', '...']

    for i, (bug_tokens, project_name, bug_report_name) in enumerate(zip(bug_reports_tokens, project_names, bug_report_names)):
        # 将错误报告的 tokens 转换为字符串
        bug_report_text = ' '.join(bug_tokens)

        # 获取对应项目下的所有源代码tokens文件
        source_files = get_source_files("source_code_tokens", project_name)

        if not source_files:
            print(f"未找到项目 {project_name} 的源代码tokens文件")
            continue

        # 准备传递给子进程的参数列表
        args_list = [
            (bug_report_text, os.path.join("source_code_tokens", project_name, source_file), stop_words)
            for source_file in source_files
        ]

        # 使用多进程池并行处理源代码文件
        with Pool(processes=4) as pool:  # 根据您的CPU核心数调整进程数量
            vsm_results = pool.map(process_source_file, args_list)

        # 按相似度从高到低排序
        vsm_results.sort(key=lambda x: x[1], reverse=True)

        # 保存结果到vsm_result文件夹中的对应错误报告txt文件
        save_vsm_result(bug_report_name, vsm_results)

        # 输出结果
        print(f"错误报告 {i} ({bug_report_name}) 的相似度分析已完成，并保存到 vsm_result/{bug_report_name}_vsm.txt")
