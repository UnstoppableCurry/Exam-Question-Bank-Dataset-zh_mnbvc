from .abstract_exam_parser import AbstractExamParser
import re

class AnnotatedExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)
    
    @staticmethod
    def detect_this_exam_type(content: str):
        lines = content.splitlines()
        if len(lines) < 10:
            return False
        answer_count = AbstractExamParser.answer_count_total(lines)
        question_indexes = AbstractExamParser.find_questions_and_answer_indexes(lines)
        return answer_count > len(question_indexes) / 2

    def extract_questions(self):
        topic_details = self.extract_topic_details()
        return [topic_detail["content"] for topic_detail in topic_details]

    
    def extract_topic_details(self):
        topic_numbers_with_content = self.find_all_topic_numbers_with_content()
        topic_details = self.construct_complete_topic_details(topic_numbers_with_content)

        topic_details = self.find_most_concentrated_increasing_subsequence(topic_details)
        return topic_details

    
    def extract_answers(self):
        topic_details = self.extract_topic_details()
        return [AnnotatedExamParser.split_question_with_answer(topic_detail["content"])["answer"] for topic_detail in topic_details]

    
    def align(self):
        topic_details = self.extract_topic_details()
        return [AnnotatedExamParser.split_question_with_answer(topic_detail["content"]) for topic_detail in topic_details]

    
    @staticmethod
    def split_question_with_answer(content):
        lines = content.splitlines()
        question_lines = []
        answer_lines = []
        is_answer = False
        
        for line in lines:
            if any(label in line for label in AnnotatedExamParser.answer_keywords):
                is_answer = True
            if is_answer:
                answer_lines.append(line.strip())
            else:
                question_lines.append(line.strip())
        
        question = "\n".join(question_lines)
        answer = "\n".join(answer_lines)
        return {"question": question, "answer": answer}
        
    def find_all_topic_numbers_with_content(self, lines=None):
        """
        根据给定的文本行列表，提取出所有的题目序号及其对应的文本内容。
        
        参数:
            lines (list): 包含题目的文本行列表。
        
        返回:
            list: 返回一个字典列表，每个字典包含"topic_number"和对应的文本内容。
            
        示例:
            输入: ['1. 问题描述...', '解析...', '2. 问题描述...', '解析...']
            输出: [{'topic_number': 1, 'content': '1. 问题描述...解析...'}, {'topic_number': 2, 'content': '2. 问题描述...解析...'}]
        """
        if not lines:
            lines = self.content.splitlines()
        pattern = rf"^\d+{'[' + '|'.join(self.topic_number_keywords) + '](?!png)'}"
        topic_details = []
        start_index = None
        topic_number = None

        for index, line in enumerate(lines):

            match = re.match(pattern, line.replace("\\",""))
            if match:
                if start_index is not None:
                    topic_details.append({"topic_number": topic_number, "content": '\n'.join(lines[start_index:index])})
                start_index = index
                topic_number = int(match.group().strip('.').strip('．').strip('、'))

        if start_index is not None:
            topic_details.append({"topic_number": topic_number, "content": '\n'.join(lines[start_index:])})
        return self.construct_complete_topic_details(topic_details)
    
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
