from .abstract_exam_parser import AbstractExamParser
import re

class StandardExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)

    
    @staticmethod
    def detect_this_exam_type(content):
        """
        校验试卷类型
        传入试卷的文本
        """
        lines = content.splitlines()
        answer_split_str = StandardExamParser.get_answer_split_str(lines[5:])
        if answer_split_str is None:
            return False
        answer_split_str_index = 0
        for i in range(len(lines)):
            if lines[i] == answer_split_str:
                answer_split_str_index = i
                break
        question_list = StandardExamParser.get_all_question_number(lines[:answer_split_str_index])
        answer_list = StandardExamParser.get_all_question_number(lines[answer_split_str_index:])
        return question_list == answer_list

    
    def extract_questions(self):
        """
        获取试卷题目
        """
        lines = self.content.splitlines()
        answer_split_str = StandardExamParser.get_answer_split_str(lines[5:])
        answer_split_str_index = 0
        for i in range(len(lines)):
            if lines[i] == answer_split_str:
                answer_split_str_index = i
                break 
        question_indexes = self.longest_increasing_subsequence_index(StandardExamParser.find_questions_and_answer_indexes(lines[:answer_split_str_index]))
        # 提取每个题目的内容
        questions_content = []
        lines = lines[:answer_split_str_index]
        for i, start_index in enumerate(question_indexes):
            # 如果不是最后一个题目，则结束索引是下一个题目的开始索引
            # 如果是最后一个题目，则内容一直取到文档的结尾
            end_index = question_indexes[i + 1] if i + 1 < len(question_indexes) else len(lines)
            # 提取当前题目的内容，包括起始索引行但不包括结束索引行
            question_content = lines[start_index:end_index]
            # 将所有行连接成一个字符串
            questions_content.append({"topic_number": StandardExamParser.extract_number_from_string('\n'.join(question_content)), "question": '\n'.join(question_content)})

        return questions_content
    
    def extract_answers(self):
        """
        获取试卷答案
        """
        lines = self.content.splitlines()
        question_list, answer_str = StandardExamParser.find_all_topic_numbers_with_content(lines)
        joined_questions = "".join(question_list[-1]['content'])
        answer_list = []
        if answer_str in joined_questions:
            # 分割字符串，获取 answer_str 右边的内容
            answer_right_side = joined_questions.split(answer_str, 1)[1]
            answer_number = 1
            while(True):
                answer, text = StandardExamParser.find_answer_by_number(answer_right_side, answer_number)
                if answer is not None:
                    answer_list.append({"topic_number":answer_number, "answer":answer})
                    answer_number = answer_number + 1
                else:
                    return answer_list
        else:
            return []

    def align(self):
        """
        对齐
        """
        return StandardExamParser.merge_questions_and_answers(self.extract_questions(),self.extract_answers())
    
    @staticmethod
    def get_all_question_number(lines):
        """
        传入试卷的每行
        返回找到的所有题号（题号不在开头也可以）
        """
        text = ''.join(lines).replace('\\', '')
        number = 1
        number_list = []
        while(number < 24):
            line, split_text = StandardExamParser.find_answer_by_number(text, number)
            if line is None:
                number = number + 1
                
                
                continue
            text = split_text
            number_list.append(number)
            number = number + 1
        return number_list
    

    @staticmethod
    def find_answer_by_number(text, number, isAdaptationSymbol=True):
        """
        寻找试卷答案通过题号
        text: 寻找题目所需文本
        number: 题目标题(1. 2. 3. 4. 5.)
        isAdaptationSymbol: 是否适配符号(默认适配 1. 2. 3.  | 不适配的话会寻找 1 2 3 4)
        """
        # 将数字转换为字符串
        number_str = str(number)
        next_number_str = str(number + 1)

        # 根据是否适配标点符号选择正则表达式
        if isAdaptationSymbol:
            # 适配符号，同时确保不是.png文件名的一部分
            pattern = re.compile(rf'({number_str}(?!\.(png|jpeg))[．.]).*?(?={next_number_str}[．.]|\Z)', re.DOTALL)
        else:
            # 不适配符号，同时确保不是.png文件名的一部分
            pattern = re.compile(rf'({number_str}(?!\.(png|jpeg))\b).*?(?={next_number_str}\b|\Z)', re.DOTALL)

        match = pattern.search(text)
        if match:
            # 匹配到的文本是当前题号到下一个题号之间的内容
            matched_text = match.group(0)
            # 剩余的文本是匹配到的内容之后的所有文本
            rest_text = text[match.end():]
            if rest_text == "":
                rest_text = text
            return matched_text, rest_text

        # 如果没有匹配，返回None和原始文本
        return None, text

    @staticmethod
    def merge_questions_and_answers(questions, answers):
        """
        入参：question的list和answers的list（格式如 extract_answers 或question的出参）
        返回对齐好的list
        """
        # 创建一个字典，将问题按照"topic_number"存储
        question_dict = {q["topic_number"]: q["question"] for q in questions}

        result = []

        # 遍历答案数组，将答案与问题组合
        for answer in answers:
            topic_number = answer["topic_number"]
            question = question_dict.get(topic_number, "")  # 获取问题，如果没有对应的问题则为空字符串
            result.append({"topic_number": topic_number, "question": question, "answer": answer["answer"]})

        # 处理只有问题而没有答案的情况
        for question in questions:
            if question["topic_number"] not in [r["topic_number"] for r in result]:
                result.append({"topic_number": question["topic_number"], "question": question["question"], "answer": ""})

        return result

    @staticmethod
    def extract_number_from_string(input_string):
        """
        传入一个字符串寻找number
        """
        pattern = r"(\d+(\.\d+)*)"  # 匹配一个或多个数字和可选的小数点
        match = re.search(pattern, input_string)
        if match:
            number_str = match.group(1)  # 获取匹配的数字部分
            return int(float(number_str))  # 将数字部分转换为浮点数，然后再转换为整数
        return None 
    
    @staticmethod
    def get_paper_question_by_number(question_indexes, lines):
        """
        传入题目的索引下标
        获取每道题 和 答案分割的字符串
        """
        question_list = []
        answer_area_str = ""
        for i, question_index in enumerate(question_indexes):
            if i+1 == len(question_indexes):
                question_list.append("".join(lines[question_indexes[i]:]))
                answer_area_str = StandardExamParser.get_answer_split_str(lines[question_indexes[i]:])
            else:
                question_list.append("".join(lines[question_index:question_indexes[i+1]]))

        return question_list,answer_area_str
    
    @staticmethod
    def get_answer_split_str(lines, answer_words = ["参考答案", "试题解析", "参考解答"]):
        """
        传入试卷文本的每一行
        返回分割的答案区域分割的位置
        """
        for line in lines:
            if any(answer_word in line for answer_word in answer_words):
                return line
        return None

    @staticmethod
    def find_questions_and_answer_indexes(lines: list[str]) -> list[super]:
        """
        获取题目和答案的lines下标

        判断行的开始是否为 数字+[. ．]
        """
        question_nums = []
        question_num_indexs = []
        pattern = r"^(\d+)[\.|\．|、]"
        for index in range(len(lines)):
            match = re.search(pattern, lines[index].replace("\\",""))
            if match: 
                question_number = match.group(1)
                question_nums.append(question_number)
                question_num_indexs.append(index)
        return [(int(x), y) for x, y in zip(question_nums, question_num_indexs)]
    
    @staticmethod
    def find_all_topic_numbers_with_content(lines):
        """
        获取标准试卷答案区
        返回每题答案的集合
        """
        question_number_indexs = AbstractExamParser.longest_increasing_subsequence_index(StandardExamParser.find_questions_and_answer_indexes(lines))
        question_list,answer_area_str = StandardExamParser.get_paper_question_by_number(question_number_indexs, lines)
        new_question_list = []
        for question in question_list:
            new_question_list.append({"topic_number":StandardExamParser.extract_number_from_string(question), "content": question})
        return StandardExamParser.construct_complete_topic_details(new_question_list),answer_area_str