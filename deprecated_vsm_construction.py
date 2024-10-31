import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_bug_tokens(base_path):

    # 存储每个项目的所有错误报告的 tokens 列表
    bug_reports_tokens = []

    # 获取所有项目的文件夹列表，排除隐藏文件和非目录
    projects = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')]

    # 按照项目名称排序，确保列表顺序一致
    projects.sort()

    for project in projects:
        project_path = os.path.join(base_path, project)

        # 存储该项目的所有 tokens
        project_tokens = []

        # 获取项目文件夹下的所有文件，排除隐藏文件
        files = [f for f in os.listdir(project_path) if not f.startswith('.')]

        # 过滤出 .txt 文件
        tokens_files = [f for f in files if f.endswith('.txt')]

        # 按照文件名排序，确保顺序一致
        tokens_files.sort()

        for tokens_file in tokens_files:
            tokens_file_path = os.path.join(project_path, tokens_file)

            # 打开并读取 tokens 文件
            with open(tokens_file_path, 'r', encoding='utf-8') as f:
                # 假设每个 tokens.txt 文件中，每个 token 占一行
                tokens = [line.strip() for line in f if line.strip()]
                # 如果 tokens 存在，则添加到项目 tokens 列表中
                if tokens:
                    project_tokens.extend(tokens)

        # 将该项目的 tokens 添加到 bug_reports_tokens 列表中
        bug_reports_tokens.append(project_tokens)

    # 打印结果
    for idx, project_tokens in enumerate(bug_reports_tokens):
        print(f"项目 {projects[idx]} 的 tokens 总数：{len(project_tokens)}")
        # 可选择打印部分 tokens 进行验证
        print(f"部分 tokens 示例：{project_tokens[:10]}")

    return bug_reports_tokens

def get_source_tokens(base_path):

    # 初始化二维数组
    source_code_tokens = []

    # 获取指定目录下的所有.txt文件，排除隐藏文件
    txt_files = [f for f in os.listdir(base_path) if f.endswith('.txt') and not f.startswith('.')]

    # 对文件名进行排序（可选，根据需要）
    txt_files.sort()

    # 遍历每个txt文件
    for filename in txt_files:
        print(f"正在处理源代码文件：{filename}")
        with open(os.path.join(base_path, filename), 'r', encoding='utf-8') as file:
            # 逐行读取文件，并去除每行的换行符和空格
            tokens = [line.strip() for line in file if line.strip()]
            # 将tokens数组添加到二维数组中
            if tokens:
                source_code_tokens.append(tokens)

    return source_code_tokens

if __name__ == '__main__':

    # tokens
    bug_reports_tokens = get_bug_tokens("bug_reports_tokens")

    source_code_tokens = get_source_tokens("source_code_tokens")

    # 将 tokens 转换为字符串
    bug_report_texts = [' '.join(tokens) for tokens in bug_reports_tokens]
    source_code_texts = [' '.join(tokens) for tokens in source_code_tokens]

    # 创建 TfidfVectorizer，移除编程语言关键字等停用词
    stop_words = ['public', 'class', 'void', 'new', 'if', 'else', 'for', 'while', 'return', '{', '}', '(', ')', ';', '...']

    vectorizer = TfidfVectorizer(stop_words=stop_words)

    # 构建文档集合
    documents = bug_report_texts + source_code_texts

    # 计算 TF-IDF 矩阵
    tfidf_matrix = vectorizer.fit_transform(documents)

    # 分割错误报告和源代码文件的向量
    num_bug_reports = len(bug_reports_tokens)
    bug_report_vectors = tfidf_matrix[:num_bug_reports]
    source_code_vectors = tfidf_matrix[num_bug_reports:]

    # 计算相似度矩阵
    similarity_matrix = cosine_similarity(bug_report_vectors, source_code_vectors)

    # 输出相似度结果
    for i, similarities in enumerate(similarity_matrix):
        print(f"错误报告 {i} 与源代码文件的相似度：")
        for j, similarity in enumerate(similarities):
            print(f"  源代码文件 {j}: 相似度 = {similarity:.4f}")
