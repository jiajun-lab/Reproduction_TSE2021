import json
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download necessary NLTK data files
nltk.download('stopwords')
nltk.download('punkt')


def preprocess_code(code_str, language):
    """
    对源代码进行预处理，进行标记化、去除特定语言关键词、分割拼接单词、去除停用词以及Porter词干提取。

    参数:
    code_str (str): 源代码字符串或错误报告字符串。
    language (str): 编程语言（如 'java'、'go'、'js'）。

    返回:
    list: 处理后的tokens列表。
    """
    # Step 1: Tokenize the code into a sequence of lexical tokens
    tokens = re.findall(r'\b\w+\b', code_str)

    # Step 2: Remove programming language-specific keywords
    programming_java_keywords = [
        'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
        'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
        'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
        'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
        'package', 'private', 'protected', 'public', 'return', 'short', 'static',
        'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
        'transient', 'try', 'void', 'volatile', 'while'
    ]

    if language == 'java':
        tokens = [token for token in tokens if token.lower() not in programming_java_keywords]

    # Step 3: Split concatenated words based on camelCase and underscores
    split_tokens = []
    for token in tokens:
        # Split by underscores (snake_case)
        subtokens = re.split(r'_', token)
        for subtoken in subtokens:
            # Split camelCase words
            camel_case_tokens = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])', subtoken)
            split_tokens.extend(camel_case_tokens)

    # Convert all tokens to lowercase
    split_tokens = [token.lower() for token in split_tokens]

    # Step 4: Remove stop words using NLTK's stop words list
    stop_words = set(stopwords.words('english'))
    tokens_no_stopwords = [token for token in split_tokens if token not in stop_words]

    # Step 5: Perform Porter stemming to derive the common base form
    porter = PorterStemmer()
    stemmed_tokens = [porter.stem(token) for token in tokens_no_stopwords]

    return stemmed_tokens


def analyze_project_source_code(source_code_directory, language):
    """
    遍历指定目录中的所有源代码文件，将每个文件的令牌单独保存到对应的txt文件中。

    参数：
    source_code_directory (str): 源代码目录的路径。
    language (str): 编程语言（如 'java'）。
    """
    # 创建 source_code_tokens 目录（如果不存在）
    output_base_dir = 'source_code_tokens'
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(source_code_directory):
        for file in files:
            if file.endswith('.' + language):
                file_path = os.path.join(root, file)

                # 相对路径
                relative_path = os.path.relpath(file_path, source_code_directory)

                # 处理代码
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_str = f.read()
                    tokens = preprocess_code(code_str, language)

                # 获取项目名称和类名
                project_name = os.path.basename(source_code_directory)
                class_name = os.path.splitext(file)[0]

                # 创建项目目录
                project_dir = os.path.join(output_base_dir, project_name)
                if not os.path.exists(project_dir):
                    os.makedirs(project_dir)

                # 创建类名_tokens.txt 文件
                output_file = os.path.join(project_dir, f"{class_name}_tokens.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    # 写入相对路径作为第一行
                    f.write(relative_path + '\n')
                    # 写入处理后的tokens
                    f.write('\n'.join(tokens))

                print(f"已处理并保存：{output_file}")


if __name__ == "__main__":
    # 指定源代码的目录路径
    source_code_directory = '/Users/lijiajun/Desktop/RA/program/pathidea/zookeeper'  # 请将此路径替换为您的实际路径
    language = 'java'

    # 分析并处理源代码
    analyze_project_source_code(source_code_directory, language)
