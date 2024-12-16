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
    Analyzes source code files and error reports by tokenizing the code,
    removing programming language-specific keywords, splitting concatenated words,
    removing stop words, and performing Porter stemming.

    Parameters:
    code_str (str): The source code or error report as a string.

    Returns:
    list: A list of processed tokens.
    """
    # Step 1: Tokenize the code into a sequence of lexical tokens
    tokens = re.findall(r'\b\w+\b', code_str)

    # Step 2: Remove programming language-specific keywords

    programming_java_keywords = [
        # Java keywords (add more keywords for other languages if needed)
        'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
        'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
        'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
        'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
        'package', 'private', 'protected', 'public', 'return', 'short', 'static',
        'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
        'transient', 'try', 'void', 'volatile', 'while'
    ]

    go_keywords = [
        'break', 'default', 'func', 'interface', 'select', 'case', 'defer', 'go',
        'map', 'struct', 'chan', 'else', 'goto', 'package', 'switch', 'const',
        'fallthrough', 'if', 'range', 'type', 'continue', 'for', 'import',
        'return', 'var'
    ]

    javascript_keywords = [
        'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
        'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
        'if', 'import', 'in', 'instanceof', 'let', 'new', 'return', 'super',
        'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with',
        'yield'
    ]
    if language == 'java':
        tokens = [token for token in tokens if token.lower() not in programming_java_keywords]
    elif language == "go":
        tokens = [token for token in tokens if token.lower() not in go_keywords]
    elif language == 'js':
        tokens = [token for token in tokens if token.lower() not in javascript_keywords]

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


def process_json(bug_report, language):
    fields = bug_report.get('fields', {})
    summary = fields.get('summary', '')
    description = fields.get('description', '')

    # 确保 summary 和 description 为字符串
    summary = summary if isinstance(summary, str) else ''
    description = description if isinstance(description, str) else ''

    text_to_process = summary + ' ' + description

    # 检查 description 是否包含日志或堆栈跟踪的格式
    # log_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \[.*?\] (DEBUG|ERROR|INFO|WARN) .*'
    # stack_trace_pattern = r'(?:Exception|Error|at\s).*(\n\s*at .*)+'
    log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) ([\w\.]+): (.+)'
    stack_trace_pattern = r'at ([\w\.]+)\(([\w]+\.java):\d+\)'
    if re.search(log_pattern, description) or re.search(stack_trace_pattern, description, re.MULTILINE):
        processed_tokens = preprocess_code(text_to_process, language)
        return processed_tokens

    return None


if __name__ == "__main__":
    '''
        处理bug_reports并保存为bug_reports_tokens
    '''
    projects = ["ActiveMQ", "Hadoop", "HDFS", "MAPREDUCE", "Hive", "Storm", "YARN", "Zookeeper"]
    for project in projects:
        directory = '../ProcessData/bug_reports/'+ project + '/details'

        items = os.listdir(directory)

        # 仅获取文件，忽略文件夹
        files = [item.strip('.json') for item in items if os.path.isfile(os.path.join(directory, item))]
        print(files)

        for name in files:
            with open('../ProcessData/bug_reports/' + project + '/' + name + '.json', 'r') as f:
                data = json.load(f)

            processed_tokens = process_json(data, 'java')
            if processed_tokens is not None and len(processed_tokens) > 0:
                with open('../ProcessData/bug_reports_tokens/'+ project + name + '_token.txt', 'w') as f:
                    f.write('\n'.join(processed_tokens))

