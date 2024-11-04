# Reproduction
reproduction (TSE2021)

- [x] 构建VSM矩阵
- [x] 分析日志和堆栈跟踪
- [ ] 分析并重建执行路径
- [ ] 项目优化

## 1. 复现流程

### 1.1 构建VSM矩阵

1. 从github上获取开源数据

   ```
   │
   ├── bug_reports:				List of bug reports
   │   ├── ActiveMQ	
   │   ├── ├── AMQ-100.json			Bug report basic content
   │   │   ├── comments				Comments for each associated bug report
   │   │   └── details				Details for each associated bug report
   │   ├── ...
   ├── vsm						VSMScore after normalization
   ├── code_changes				Detailed Java file changes for each bug report 
   ├── vsm_segmentation				Per-file score at different segmentation size
   ├── log						List of logged classes extracted from bug reports
   └── path					List of classes that are found on the execution paths
   ```
   
2. 处理bug_reports中每个项目的错误报告

   1. 筛选bug_reports中summary、description中含有日志相关信息和堆栈跟踪信息的错误报告，作为日志分析和路径重建的原始数据。

   2. 删除错误报告中的特定关键字。

   3. 根据驼峰命名法和下划线拆分串联词，并使用Python中NLTK库删除停用词。

   4. 执行Porter词干提取，获得单词的基本形式。

   5. 通过以上三个步骤可以获得每个错误报告的语料库集合。

   6. ```
      bug_reports_tokens/
      ├── ActiveMQ  activemq bug report tokens
      ├── HDFS			hdfs bug report tokens
      ├── Hadoop    hadoop bug report tokens
      ├── Hive      hive bug report tokens
      ├── MAPREDUCE mapreduce bug report tokens
      ├── Storm     storm bug report tokens
      ├── YARN      yarn bug report tokens
      └── Zookeeper zookeeper bug report tokens
      ```

      

3. 获得源代码，本论文共涉及八个开源系统：

   1. ActiveMQ(5.15.13)：https://archive.apache.org/dist/activemq/5.15.13/
   2. Hadoop(2.7.6)：https://github.com/apache/hadoop
   3. HDFS(2.7.0)：https://github.com/apache/hadoop 见hadoop-hdfs-project
   4. Hive(2.7.0)：https://archive.apache.org/dist/hive/hive-3.0.0/ 未找到hive2.7.0的release，先使用3.0.0版本进行实验
   5. MapReduce(3.1.4)：https://github.com/apache/hadoop 见hadoop-mapreduce-project
   6. Storm(2.2.0)：https://archive.apache.org/dist/storm/apache-storm-2.2.0/
   7. Yarn(3.1.2)：https://github.com/apache/hadoop 见Hadoop-yarn-project
   8. Zookeeper(3.6.0)：https://archive.apache.org/dist/zookeeper/zookeeper-3.6.0/

4. 处理源代码中每个java文件

   1. 同bug_reports中的处理方式

   2. 获得每个项目中java文件的tokens

   3. ```
      source_code_tokens/
      ├── ActiveMQ  activemq source code tokens
      ├── HDFS			hdfs source code tokens
      ├── Hadoop    hadoop source code tokens
      ├── Hive      hive source code tokens
      ├── MAPREDUCE mapreduce source code tokens
      ├── Storm     storm source code tokens
      ├── YARN      yarn source code tokens
      └── Zookeeper zookeeper source code tokens
      ```

5. 将每个项目的错误报告tokens与该项目的java文件的tokens计算余弦相似度得分并排序，将得分结果与开源数据的vsm的数据进行比较，将得分结果存入vsm_result。

6. 实现情况，目前已经完成八个系统的带有日志和堆栈跟踪信息的错误报告的vsm得分计算。

### 1.2 分析日志片段和堆栈跟踪信息

1. 对1.1中第二步筛选出来的错误报告进行日志和堆栈跟踪信息进行提取，这里使用正则表达式进行筛选。

   ```python
   log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) ([\w\.]+): (.+)'
   stack_trace_pattern = r'at ([\w\.]+)\(([\w]+\.java):\d+\)'
   ```

2. 为日志片段中的每个文件分配固定分数0.1，在堆栈跟踪（Stack Trace）中，**越靠近底部（即最早被调用）的文件或方法更可能是问题的根源**。这意味着堆栈跟踪中**最底部的文件**往往是导致异常或错误的根本原因所在。所以首先对堆栈跟踪进行提取后进行反转，再为堆栈跟踪中出现的文件分配1/rank的分数，第十名即以后的文件分配分数固定为0.1。

3. 合并输出日志得分

4. 实现情况，目前已经完成八个系统的带有日志和堆栈跟踪信息的错误报告的log得分计算。

### 1.3 分析和重建执行路径



## 2.论文实现优化

idea：

1. 对第一步相似度分析使用大模型替代原有使用基于词频的vsm比较方法
2. 
