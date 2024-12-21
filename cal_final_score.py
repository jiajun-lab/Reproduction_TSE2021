import os


def extract_name(file_name):
    return file_name.split("_")[0]


def read_file_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                l = line.strip('\n')
                l = l.split(": ")
                l[1] = float(l[1])
        return l
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


def add_scores(vsm_path, log_path, path_path, output_path):
    """
    对三个文件夹中编号相同的文件逐行相加。
    Args:
        vsm_path (str): VSMScore 文件夹路径。
        log_path (str): LogScore 文件夹路径。
        path_path (str): PathScore 文件夹路径。
        output_path (str): 输出结果文件夹路径。
    """
    # 提取文件编号
    vsm_files = {extract_name(file): file for file in os.listdir(vsm_path)}
    log_files = {extract_name(file): file for file in os.listdir(log_path)}
    path_files = {extract_name(file): file for file in os.listdir(path_path)}

    # 找到编号相同的文件
    common_ids = set(vsm_files.keys()) & set(log_files.keys()) & set(path_files.keys())

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_id in common_ids:
        vsm_file = os.path.join(vsm_path, vsm_files[file_id])
        log_file = os.path.join(log_path, log_files[file_id])
        path_file = os.path.join(path_path, path_files[file_id])
        output_file = os.path.join(output_path, f"{file_id}_total_score.txt")

        # 读取每个文件的分数
        vsm_scores = read_file_lines(vsm_file)
        log_scores = read_file_lines(log_file)
        path_scores = read_file_lines(path_file)

        # 逐行相加
        total_scores = []
        for class_path, vsm_score in vsm_scores:
            class_name = class_path.split("/")[-1]  # 提取类名

            # 初始化类路径的得分
            if class_path not in total_scores:
                total_scores[class_path] = 0.0
            total_scores[class_path] += vsm_score  # 累加 VSM 分数

            # 内层匹配 log_scores
            for log_class_path, log_score in log_scores:
                if log_class_path == class_path or log_class_path == class_name:
                    total_scores[class_path] += log_score

            # 内层匹配 path_scores
            for path_class_path, path_score in path_scores:
                if path_class_path == class_path or path_class_path.split("/")[-1] == class_name:
                    total_scores[class_path] += path_score

            # 转换为最终格式 [类路径, 总得分]
        final_scores = [[key, value] for key, value in total_scores.items()]

        # 写入结果
        write_file_lines(output_file, final_scores)
        print(f"Processed and saved: {output_file}")


def write_file_lines(file_path, lines):
    """
    将结果写入文件。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(f"{line}\n")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")


if __name__ == "__main__":
    vsm_path = "../pathidea/ProcessData/vsm_result"
    log_path = "../pathidea/ProcessData/log_result"
    path_path = "../pathidea/ProcessData/path_results"
    output_path = "../pathidea/ProcessData/total_scores"

    add_scores(vsm_path, log_path, path_path, output_path)