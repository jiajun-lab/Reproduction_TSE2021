import os
import evaluation


def extract_name(file_name):
    return file_name.split("_")[0]


def read_file_lines(file_path):
    result = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                l = line.strip('\n')
                l = l.split(": ")
                l[1] = float(l[1])
                result.append(l)
        return result
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


def process_vsm_scores(vsm_result):
    vsm_process_result = {}
    for item in vsm_result:
        vsm_score = float(item[1])
        vsm_process_result[item[0]] = vsm_score
    return vsm_process_result

def add_scores(vsm_path, log_path, path_path, output_path):
    # 提取文件编号
    vsm_files = {extract_name(file): file for file in os.listdir(vsm_path)}
    log_files = {extract_name(file): file for file in os.listdir(log_path)}
    path_files = {extract_name(file): file for file in os.listdir(path_path)}

    # 如果输出路径不存在，则创建
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_id, vsm_file_name in vsm_files.items():
        # 获取对应的文件路径
        vsm_file = os.path.join(vsm_path, vsm_file_name)
        log_file = os.path.join(log_path, log_files[file_id]) if file_id in log_files else None
        path_file = os.path.join(path_path, path_files[file_id]) if file_id in path_files else None
        output_file = os.path.join(output_path, f"{file_id}_total_score.txt")

        # 读取每个文件的分数
        vsm_scores = process_vsm_scores(read_file_lines(vsm_file))
        log_scores = read_file_lines(log_file) if log_file else []
        path_scores = read_file_lines(path_file) if path_file else []

        # 逐行累加得分
        total_scores = {}
        for class_path, vsm_score in vsm_scores.items():
            class_name = class_path.split("/")[-1]  # 提取类名

            # 初始化类路径的得分
            if class_path not in total_scores:
                total_scores[class_path] = 0.0
            total_scores[class_path] += vsm_score  # 累加 VSM 分数

            # 匹配并累加 log_scores
            for log_class_path, log_score in log_scores:
                if log_class_path == class_path or log_class_path.split("/")[-1] == class_name:
                    total_scores[class_path] += log_score

            # 匹配并累加 path_scores
            for path_class_path, path_score in path_scores:
                if path_class_path == class_path or path_class_path.split("/")[-1] == class_name:
                    total_scores[class_path] += path_score

        # 转换为最终格式 [类路径, 总得分]
        final_scores = sorted(
            [[key, value] for key, value in total_scores.items()],
            key=lambda x: x[1],  # 按照第二项 (value) 排序
            reverse=True  # 设置为 True 表示降序排序，False 为升序
        )

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