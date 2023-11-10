from abc import ABC, abstractmethod
import re

class AbstractExamParser(ABC):
    answer_keywords=["答案"]
    topic_number_keywords=[".", '．', '、']

    def __init__(self, content):
        self.content = content

    @staticmethod
    @abstractmethod
    def detect_this_exam_type(content):
        """
        检测试卷的类型是否为此类。
        
        此方法应该分析试卷的内容，识别并返回试卷的具体类型。
        
        返回:
            bool: 是否为当前类可以解析的类型
        """
        pass

    @abstractmethod
    def extract_questions(self):
        """
        提取试卷中的题目。
        
        此方法应该从试卷内容中提取出所有的题目。
        
        返回:
            list: 包含所有题目，每个元素是一个question。
        """
        pass

    @abstractmethod
    def extract_answers(self):
        """
        提取试卷中的答案。
        
        此方法应该从试卷内容中提取出所有的答案。
        
        返回:
            list: 包含所有答案，每个元素是一个answer。
        """
        pass

    @abstractmethod
    def align(self):
        """
        对齐试卷的题目和答案。
        
        此方法应该确保每个题目与其对应的答案正确对齐，以便于阅卷或其他处理。
        """
        pass
    
    @staticmethod
    def check_contains_answers(content):
        """检测试卷是否存在答案"""
        """Todo: 不完整"""
        lines = content.splitlines()
        answer_count = AbstractExamParser.answer_count_total(lines)
        return answer_count > 0
    
    @staticmethod
    def answer_count_total(lines):
        """
        统计answer_keywords在试卷中每一行中出现的总次数
        """
        # 每道题的索引下标
        answer_count = 0
        for line in lines:
            if any(keyword in line for keyword in AbstractExamParser.answer_keywords):
                answer_count += 1
        return answer_count
    
    @staticmethod
    def find_questions_and_answer_indexes(lines: list[str]) -> list[int]:
        indexes = []
        pattern = r"^\d+[\.|\．|、]"
        for index in range(len(lines)):
            match = re.search(pattern, lines[index].replace("\\",""))
            if match: 
                indexes.append(index)
        return indexes 

    @staticmethod
    def split_topic_details_content(content, next_topic_number):
        """
        根据下一个题目编号，将给定内容分为两部分。
        
        参数:
            content (str): 当前的题目内容
            next_topic_number (int): 下一个题目的编号
            
        返回:
            tuple: (before_topic_content, after_topic_content)
        """
        # 定义匹配题目编号的正则表达式
        pattern = rf"\d+{'[' + '|'.join(['.', '．', '、']) + ']'}"
        lines = content.splitlines()
        
        before_topic_content = []
        after_topic_content = []
        split_flag = False
        
        for line in lines:
            match = re.search(pattern, line)
            if match:
                current_topic_number = int(match.group().strip('.').strip('．').strip('、'))
                if current_topic_number == next_topic_number:
                    split_flag = True

            if split_flag:
                after_topic_content.append(line)
            else:
                before_topic_content.append(line)

        return "\n".join(before_topic_content), "\n".join(after_topic_content)
    
    @staticmethod
    def longest_increasing_subsequence_index(nums):
        n = len(nums)
        dp = [[i] for i in range(n)]

        for i in range(n):
            for j in range(i):
                if nums[j][0] < nums[i][0]:
                    if len(dp[j]) + 1 > len(dp[i]) or (len(dp[j]) + 1 == len(dp[i]) and dp[j][-1] == dp[i][-1] - 1):
                        dp[i] = dp[j] + [i]

        dp = list(filter(lambda lis: nums[lis[0]][1] < len(nums) / 2, dp))
        dp = sorted(dp, key=lambda lis: len(lis), reverse=True)
        return [nums[i][1] for i in dp[0]]

    @staticmethod
    def find_most_concentrated_increasing_subsequence(topic_details):
        nums = [(detail['topic_number'], idx) for idx, detail in enumerate(topic_details)]
        # Get the indices of the longest increasing subsequence
        lis_indices = AbstractExamParser.longest_increasing_subsequence_index(nums)

        # Extract the subsequence from the topic_details using the indices
        return [topic_details[idx] for idx in lis_indices]
    
    @staticmethod
    def construct_complete_topic_details(topic_details):
        """
        根据题目详情列表构建完整的题目详情列表，处理非连续的题目编号。
        
        参数:
            topic_details (list): 原始题目详情列表
            
        返回:
            list: 完整的题目详情列表
        """
        complete_topic_details = []

        for index, detail in enumerate(topic_details):
            topic_number = detail["topic_number"]
            content = detail["content"]

            # 如果是最后一个元素
            if index == len(topic_details) - 1:
                complete_topic_details.append(detail)
                break

            next_topic_number = topic_details[index+1]["topic_number"]

            # 处理连续的题目编号
            if topic_number + 1 == next_topic_number:
                complete_topic_details.append(detail)
                continue

            # 处理非连续的题目编号
            while topic_number < next_topic_number:
                # 分割当前内容
                before_topic_content, after_topic_content = AbstractExamParser.split_topic_details_content(content, topic_number + 1)

                # 将当前题目内容添加到完整列表中
                complete_topic_details.append({"topic_number": topic_number, "content": before_topic_content})

                # 如果后续没有内容，则退出循环
                if not after_topic_content:
                    break

                # 否则，增加题目编号并设置下一次迭代的内容
                topic_number += 1
                content = after_topic_content

        return complete_topic_details