# Reproduction_Pathidea
reproduction of Pathidea(TSE2021)

- [x] 构建VSM矩阵
- [ ] 分析日志和堆栈跟踪
- [ ] 分析并重建执行路径
- [ ] 项目优化

## 1. 复现流程

### 1.1 构建VSM矩阵

1. 从github上获取pathidea开源数据：https://github.com/SPEAR-SE/Pathidea_Data.git

   ```
   Pathidea_Data
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

   1. 删除错误报告中的特定关键字。

   2. 根据驼峰命名法和下划线拆分串联词，并使用Python中NLTK库删除停用词。

   3. 执行Porter词干提取，获得单词的基本形式。

   4. 通过以上三个步骤可以获得每个错误报告的语料库集合。

   5. ```
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
   2. Hadoop(2.7.6)：https://archive.apache.org/dist/hadoop/common/hadoop-2.7.6/
   3. HDFS(2.7.0)：https://archive.apache.org/dist/hadoop/common/hadoop-2.7.0/见hadoop-hdfs-project
   4. Hive(2.7.0)：https://archive.apache.org/dist/hive/hive-3.0.0/ 未找到hive2.7.0的release，先使用3.0.0版本进行实验
   5. MapReduce(3.1.4)：https://archive.apache.org/dist/hadoop/common/hadoop-3.1.4/见hadoop-mapreduce-project
   6. Storm(2.2.0)：https://archive.apache.org/dist/storm/apache-storm-2.2.0/
   7. Yarn(3.1.2)：https://archive.apache.org/dist/hadoop/common/hadoop-3.1.2/见Hadoop-yarn-project
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

5. 将每个项目的错误报告tokens与该项目的java文件的tokens计算余弦相似度得分并排序，将得分结果与pathidea开源数据的vsm的数据进行比较，将得分结果存入vsm_result。

6. 实现情况，目前已经完成ActiveMQ、HDFS、Hadoop错误报告的vsm得分计算。

### 1.2 分析日志片段和堆栈跟踪系统

### 1.3 分析和重建执行路径



## 2.论文实现优化
