import os
import json


def normalize_vsm_scores(vsm_scores):
    """
    归一化 VSMScore 到 0 到 1 之间.
    Args:
        vsm_scores (dict): 文件路径 -> VSMScore 映射.
    Returns:
        dict: 归一化后的 VSMScore 映射.
    """
    min_score = min(vsm_scores.values())
    max_score = max(vsm_scores.values())

    if max_score == min_score:  # 避免除零
        return {file: 1.0 for file in vsm_scores}

    # 归一化公式：N(x) = (x - min) / (max - min)
    return {file: (score - min_score) / (max_score - min_score) for file, score in vsm_scores.items()}


def read_buggy_files(json_file):
    """
    读取 JSON 文件并解析错误报告及其相关的 buggy 文件。
    Args:
        json_file (str): JSON 文件的路径。
    Returns:
        dict: 错误报告名称（键）及其对应的 buggy 文件列表（值）。
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        parsed_data = {}
        for key, value in data.items():
            report_name = key.split("@")[0]  # 获取错误报告名
            parsed_data[report_name] = value
        return parsed_data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return {}


def calculate_top_n(rank_list, buggy_files, n):
    """
    计算 TopN 指标，包括 Precision@N 和 Recall@N
    Args:
        rank_list (list): 排名结果，按优先级从高到低排序。
        buggy_files (list): 实际 buggy 文件列表。
        n (int): N 的值，表示取前 N 项。
    Returns:
        dict: 包含 Precision@N、Recall@N 和 F1@N 的结果字典。
    """
    rank_list = [item[0].split("/")[-1] for item in rank_list]
    top_n_files = rank_list[:n]
    buggy_files_set = set([file.split(".")[-1]+".java" for file in buggy_files])

    # Precision@N
    precision = len(set(top_n_files) & buggy_files_set) / len(top_n_files) if top_n_files else 0.0
    # Recall@N
    recall = len(set(top_n_files) & buggy_files_set) / len(buggy_files_set) if buggy_files_set else 0.0
    # F1@N
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "Precision@N": precision,
        "Recall@N": recall,
        "F1@N": f1
    }


def average_precision(rank_list, buggy_files):
    """
    计算 Average Precision (AP)
    Args:
        rank_list (list): 排名列表。
        buggy_files (set): buggy 文件集合。
    Returns:
        float: 平均精度 (AP)。
    """
    correct_files = 0
    precision_sum = 0.0
    rank_list = [item[0].split("/")[-1] for item in rank_list]
    buggy_files = set([file.split(".")[-1] + ".java" for file in buggy_files])
    for idx, file in enumerate(rank_list):
        if file in buggy_files:
            correct_files += 1
            precision_sum += correct_files / (idx + 1)  # i / Pos(i)
    return precision_sum / len(buggy_files) if buggy_files else 0.0


def calculate_reciprocal_rank(rank_list, buggy_files):
    """
    计算 Reciprocal Rank (RR)
    Args:
        rank_list (list): 排名列表。
        buggy_files (set): buggy 文件集合。
    Returns:
        float: Reciprocal Rank。
    """
    rank_list = [item[0].split("/")[-1] for item in rank_list]
    buggy_files = set([file.split(".")[-1] + ".java" for file in buggy_files])
    for idx, file in enumerate(rank_list):
        if file in buggy_files:
            return 1 / (idx + 1)
    return 0.0


def compute_project_metrics(total_score_path, code_change_dict, project_names, n):
    """
    计算每个项目的总体 Precision, Recall, F1, MAP 和 MRR。
    Args:
        total_score_path (str): 总得分文件夹路径。
        code_change_dict (dict): 错误报告和 buggy 文件的字典。
        project_names (list): 项目名称前缀列表。
        n (int): Top N 的值。
    Returns:
        dict: 每个项目的 Precision, Recall, F1, MAP 和 MRR 的平均值。
    """
    total_score_files = os.listdir(total_score_path)
    project_metrics = {project: {"Precision@N": 0.0, "Recall@N": 0.0, "F1@N": 0.0, "MAP": 0.0, "MRR": 0.0, "Count": 0}
                       for project in project_names}

    for report_name, buggy_files in code_change_dict.items():
        prefix = report_name.split("-")[0]  # 获取前缀
        if prefix in project_names:
            for total_score_file in total_score_files:
                if report_name in total_score_file:
                    # 读取排名结果文件
                    rank_list = []
                    with open(os.path.join(total_score_path, total_score_file), 'r') as f:
                        for line in f.readlines():
                            line = line.strip()[2:-2]
                            rank_list.append(line.split("', "))

                    # 计算 TopN 指标
                    metrics = calculate_top_n(rank_list, buggy_files, n)

                    # 计算 AP 和 Reciprocal Rank
                    ap = average_precision(rank_list, buggy_files)
                    rr = calculate_reciprocal_rank(rank_list, buggy_files)

                    # 累加到对应的项目
                    project_metrics[prefix]["Precision@N"] += metrics["Precision@N"]
                    project_metrics[prefix]["Recall@N"] += metrics["Recall@N"]
                    project_metrics[prefix]["F1@N"] += metrics["F1@N"]
                    project_metrics[prefix]["MAP"] += ap
                    project_metrics[prefix]["MRR"] += rr
                    project_metrics[prefix]["Count"] += 1

    # 计算每个项目的平均指标
    for project in project_names:
        count = project_metrics[project]["Count"]
        if count > 0:
            project_metrics[project]["Precision@N"] /= count
            project_metrics[project]["Recall@N"] /= count
            project_metrics[project]["F1@N"] /= count
            project_metrics[project]["MAP"] /= count
            project_metrics[project]["MRR"] /= count

    return project_metrics


if __name__ == "__main__":
    project_names = ["AMQ", "HADOOP", "HDFS", "MAPREDUCE", "YARN", "HIVE", "STORM", "ZOOKEEPER"]
    total_score_path = "../pathidea/ProcessData/total_scores"
    code_change_file = "../pathidea/Pathidea_Data/code_changes/code_change.json"

    # 读取 buggy 文件
    code_change_dict = read_buggy_files(code_change_file)
    Ns = [1, 5, 10]  # 设置 Top N 值
    aprr = {project: {"MAP": 0.0, "MRR": 0.0}
                       for project in project_names}

    for N in Ns:
        # 计算每个项目的指标
        metrics = compute_project_metrics(total_score_path, code_change_dict, project_names, N)
        # 输出结果
        print(
            f"{'Project':<15}\t{'Precision@' + str(N):<15}\t{'Recall@' + str(N):<15}\t{'F1@' + str(N):<15}\t{'MAP':<15}\t{'MRR':<15}\t{'Count':<10}")
        print("-" * 100)  # 分隔线
        for project, result in metrics.items():
            # aprr[project]["MAP"] += result["MAP"]
            # aprr[project]["MRR"] += result["MRR"]
            if project != "ZOOKEEPER":
                print(
                    f"{project:<15}\t{result['Precision@N']:<15.4f}\t{result['Recall@N']:<15.4f}\t{result['F1@N']:<15.4f}\t{result['MAP']:<15.4f}\t{result['MRR']:<15.4f}\t{result['Count']:<10}\n")
            else:
                print(
                    f"{project:<15}\t{result['Precision@N']/2:<15.4f}\t{result['Recall@N']/2:<15.4f}\t{result['F1@N']/2:<15.4f}\t{result['MAP']/2:<15.4f}\t{result['MRR']/2:<15.4f}\t{result['Count']:<10}\n"
                )
        print("\n")

    # for project, result in aprr.items():
    #     print(f"{project:<15}\t{result['MAP']/len(Ns):<15.4f}\t{result['MRR']/len(Ns):<15.4f}")