import bisect
import re
import regex
import statistics
import numpy as np


GET_TOPIC_PATTERN = re.compile(r'^(\d+)\\*[．.]|^(\\*[（(])\d+\\*[）)]|^\\*\d+\\\.|^\d+、|^\d+[ABCD] |^\[(\d+)\]|^\d+\（')
REMOVE_NOISE_CHAR = re.compile(r'image\d+\.')
GET_TOPIC_PATTERN_IN_NOT_START = regex.compile(r'(\d+)\\*[．. ]|(\\*[（(])\d+\\*[）)]|\\*\d+\\\.|\d+、|^\d+[ABCD]')


def one_file_per_process(text):
    """
    接受一个可能包含多行的文本字符串，将其拆分为行，去除每一行中的某些特定字符，移除空行，然后将清理后的行重新组合成一个单一的字符串。
    
    参数:
        text (str): 可以包含多行的文本字符串。
        
    返回:
        str: 每一行都已经被清理和重新组装的文本字符串。
    """

    liens = text.splitlines()
    liens = map(lambda x: x.replace("> ", "").replace(">", "").replace("*", "").replace("\u3000", ""), liens)
    liens = filter(lambda x: x.strip() != "", liens)
    return "\n".join(liens)


def extract_and_combine_numbers(str_val):
    """
    从给定的字符串中提取数字，它会寻找字符串中开始的题号，然后从中提取出数字字符，再将它们组合在一起。
    
    参数:
        str_val (str): 输入字符串，需要从中提取数字。
        
    返回:
        int: 从输入字符串中提取出的数字。如果没有数字，就返回0。
    """
    pattern = re.compile(r"^(\d+)\\*[．.]|^(\\*[（(])\d+\\*[）)]|^\\*\d+\\\.|^\d+、|^\d+[ABCD] |^\[(\d+)\]|^\d+\（|^\d+【")
    match = pattern.match(str_val)

    numbers = None
    if match:
        numbers = ''.join(c for c in match[0] if c.isdigit())

    return int(numbers) if numbers else None


def extract_and_combine_numbers_in_not_start(str_val):
    """
     从给定的字符串中提取数字，它会寻找字符串中任意位置开始的第一个题号，然后从中提取出数字字符，再将它们组合在一起。
    
    参数:
        str_val (str): 输入字符串，需要从中提取数字。
        
    返回:
        int: 从输入字符串中提取出的数字。如果没有数字，就返回0。
    """
    str_val = REMOVE_NOISE_CHAR.sub("", str_val)
    pattern = regex.compile(r'(\d+)\\*[．.]|(\\*[（(])\d+\\*[）)]|\\*\d+\\\.|\d+、|\d+[ABCD] |\[(\d+)\]|\d+（|\d+【')
    match = pattern.search(str_val)

    numbers = None
    if match:
        numbers = ''.join(c for c in match.group() if c.isdigit())

    return int(numbers) if numbers else None


def extract_and_combine_numbers_in_not_start_by_number(str_val, number):
    """
     从给定的字符串中提取数字，它会寻找字符串中任意位置开始的第一个题号，然后从中提取出数字字符，再将它们组合在一起。

    参数:
        str_val (str): 输入字符串，需要从中提取数字。

    返回:
        int: 从输入字符串中提取出的数字。如果没有数字，就返回0。
    """
    str_val = REMOVE_NOISE_CHAR.sub("", str_val)
    number = str(number)
    pattern = regex.compile(r'(\d+)\\*[．.]|(\\*[（(])\d+\\*[）)]|\\*\d+\\\.|\d+、|\d+[ABCD] |\[(\d+)\]|\d+（|\d+【'.replace('\d+',number))
    match = pattern.search(str_val)

    numbers = None
    if match:
        numbers = ''.join(c for c in match.group() if c.isdigit())

    return int(numbers) if numbers else None

def longest_increasing_subsequence_index(topics):
    """
    获取一个列表中的最长递增子序列的索引。首先，它从主题列表中提取数字，然后找到最长的递增子序列，只返回开始位置在topics长度一半之前的。
    
    参数:
        topics (list): 包含一系列题目的列表，这个题目列表应该是不完全正确的
        deviation: 允许在最长的公众序列中
        
    返回:
        list: 最长递增子序列的索引列表。
    """
    # Use a list of tuples, where each tuple contains the number and its index in the original list
    nums = [(extract_and_combine_numbers(topic), i) for i, topic in enumerate(topics) if extract_and_combine_numbers(topic) is not None]
    
    topics = nums
    if not nums:
        return []

    n = len(nums)
    dp = [[i] for i in range(n)]

    for i in range(n):
        for j in range(i):
            if nums[j][0] < nums[i][0]:
                if len(dp[j]) + 1 > len(dp[i]) or (len(dp[j]) + 1 == len(dp[i]) and dp[j][-1] == dp[i][-1] - 1):
                    dp[i] = dp[j] + [i]

    # We need to filter based on the original index, not the index in the nums list
    dp = list(filter(lambda lis:nums[lis[0]][1] < len(topics)/2, dp))
    dp = list(sorted(dp, key=lambda lis:len(lis), reverse=True))
    # Return the original indices, not the indices in the nums list
    return [nums[i][1] for i in dp[0]]


ANSWER_WORDS = ["答案", "参考答案", "试题解析", "参考解答"]
ANSWER_IN_QUESTION_WORDS = ["答案", "答", "解"]

def find_answer_split_str(all_question):
    """
    在试卷中寻找答案的位置，返回一个标志值或用于分隔答题区和答案区的字符串。
    
    参数:
        all_question (list): 包含所有问题的列表。
        
    返回:
        int/str: 返回一个标志值或用于分隔答题区和答案区的字符串。如果试卷无答案返回0，答案在每道试题下方返回1，如果答案在一个特定的区域，返回该区域的开始行。
    """

    occurrence_number = 0
    for question in all_question:
        if any(answer_word in question for answer_word in ANSWER_IN_QUESTION_WORDS):
            # print(question)
            # print("==============")
            occurrence_number += 1

    if occurrence_number == 0:
        return 0

    if occurrence_number > len(all_question) / 2:
        return 1

    for line in all_question[-1].split("\n"):
        if any(answer_word in line for answer_word in ANSWER_WORDS):
            return line

    return -1


def find_next_question_index(start, lines):
    """
    从给定的开始位置搜索下一道题目的索引。
    
    参数:
        start (int): 搜索的开始位置。
        lines (list): 包含所有行的列表。
        
    返回:
        int: 下一道题目的索引位置。如果没有更多的题目，就返回行列表的长度（即：返回到行列表的末尾）。
    """

    for index in range(start + 1, len(lines)):
        match = GET_TOPIC_PATTERN.match(lines[index])

        if match:
            return index

    return len(lines)


def generate_answer_area_string(text: str, split_str):
    splited_text = text.split(split_str)

    splited_text = list(filter(lambda x:x.replace(" ","") != "", splited_text))
    return None if len(splited_text) == 1 else "\n".join(splited_text[1:])


def answer_area_str_process(text):
    '''
    对包含答案的文本进行处理，主要是对每一行的处理。如果一行以中文数字开始，那么就提取该行第一个阿拉伯数字以后的内容，否则就保留该行。

    Args:
    text: 一个包含答案的文本。

    Returns:
    result: 一个处理后的字符串，每一行都已经进行了处理。
    '''

    lines = text.split('\n')
    result = []
    for line in lines:
        # 检查每一行是否以中文数字开始
        if re.match('^[一二三四五六七八九十]', line):
            line = REMOVE_NOISE_CHAR.sub("", line)
            matches = GET_TOPIC_PATTERN_IN_NOT_START.findall(line)
            # 如果找到匹配，那么就提取该行第一个匹配以后的内容
            if matches:
                first_match = matches[0][0] if matches[0][0] != '' else matches[0][1]
                pos = line.find(first_match)
                result.append(line[pos:].strip())
        else:
            # 如果一行不是以中文数字开始，那么就保留该行
            result.append(line.strip())
    return "\n".join(result)


def match_specific_from_end(text, number):
    '''
    从文本的末尾开始，匹配特定的数字。

    Args:
    text: 需要匹配的文本。
    number: 需要匹配的数字。

    Returns:
    返回一个元组，包含三个元素。第一个元素是匹配的文本，第二个元素是移除匹配部分后的剩余文本，第三个元素是文本开始的数字。如果没有匹配，那么返回(None, None, None)。
    '''
    text = REMOVE_NOISE_CHAR.sub("", text)
    pattern = regex.compile(r'(\d+\\*[．. ]|\\*[（(]\d+\\*[）)]|^\\*\d+\\\.|^\d+、|\d+[ABCD])')

    matches = [m for m in pattern.finditer(text)]

    if matches:
        specific_match = None
        for match in reversed(matches):  # 反向列表，从末尾开始匹配
            match_number = int(re.search(r'\d+', match.group()).group())
            if match_number == number:
                specific_match = match
                break
        if specific_match is None:
            return None, None, None
        else:
            # 在完整文本中匹配第一个符合模式的数字
            text = REMOVE_NOISE_CHAR.sub("", text)
            start_match = GET_TOPIC_PATTERN.search(text)
            if start_match:
                match_group = start_match.group()
            else:
                start_match = GET_TOPIC_PATTERN_IN_NOT_START.search(text)
                match_group = start_match.group()

            start_number = int(re.search(r'\d+', match_group).group())  # 提取数字部分
            remaining_text = text[:specific_match.start()]  # 移除匹配部分后的剩余文本
            return text[specific_match.start():], remaining_text, start_number
    else:
        return None, None, None


def match_specific_from_start(text, number):
    '''
    从文本的开始，匹配特定的数字。

    Args:
        text (str): 需要匹配的文本。
        number (int): 需要匹配的数字。

    Returns:
        tuple: 返回一个元组，包含两个元素。
               第一个元素是匹配的文本，第二个元素是匹配到的所有文本（包括当前行）。
               如果没有匹配，返回 (None, None)。
    '''
    lines = text.splitlines()
    number = str(number)

    pattern = re.compile(r'(\d+)\\*( [．.])|(\\*[（(])\d+\\*[）)]|\\*\d+\\\.|\d+、|\d+[ABCD] |\[(\d+)\]|\d+（|\d+【'.replace('\d+',number))
    for index, line in enumerate(lines):

        match = pattern.search(line)
        if match:
            return "\n".join(lines[:index]), "\n".join(lines[index:])

    return None, None


def refine_answers(raw_answer_list):
    '''
    对一个包含未完全处理好的答案列表进行重新拆分，以使其更为完整。

    Args:
    raw_answer_list: 一个包含未完全处理好的答案的列表。

    Returns:
    refined_answers: 一个包含重新处理过的答案的列表。
    '''

    refined_answers = []
    reversed_answers = raw_answer_list[::-1]

    # 对反向答案列表中的每一个答案进行遍历
    for index, current_answer in enumerate(reversed_answers):
        # 获取下一个题目的序号，如果当前题目是列表中的最后一个，
        # 那么下一个题目的序号应该是列表中的第一个题目的序号
        if index >= len(reversed_answers) - 1:
            next_topic_number = extract_and_combine_numbers(raw_answer_list[0])
        else:
            # 否则，下一个题目的序号应该是当前题目在反向列表中的下一个题目的序号
            next_topic_number = extract_and_combine_numbers(reversed_answers[index + 1])

        # 获取当前答案对应的题目序号
        current_topic_number = extract_and_combine_numbers(current_answer)

        # 从答案的末尾开始查找，尝试匹配题目序号+1的答案
        previous_answer, remaining_text, start_number = match_specific_from_end(current_answer,
                                                                                current_topic_number + 1)

        # 如果找到了匹配的答案，那么将剩余的文本添加到所有答案的列表中
        if previous_answer:
            refined_answers.append(remaining_text)
        else:
            # 否则，直接将当前答案添加到所有答案的列表中
            refined_answers.append(current_answer)

        # 计算逻辑上的上一道题的题目序号（如现在是20题，那么"previous_topic_number"应该等于19）
        previous_topic_number = current_topic_number - 1

        # 如果下一序列的道题的题目序号等于逻辑上的上一道题的题目序号，那么继续下一次循环
        if next_topic_number == previous_topic_number:
            continue

        # 否则，将反向答案列表中的剩余部分合并成一段文本
        search_text = "/n".join(reversed_answers[:index:-1])

        # 当下一道题的题目序号小于上一道题的题目序号时，进入循环
        while next_topic_number < previous_topic_number:
            # 从文本的末尾开始查找，尝试匹配上一道题的题目序号的答案
            previous_answer, remaining_text, start_number = match_specific_from_end(search_text, previous_topic_number)

            # 如果没有找到匹配的答案
            if not previous_answer:
                refined_answers.append(search_text)
                break

            # 如果找到了匹配的答案，那么将该答案添加到所有答案的列表中
            refined_answers.append(previous_answer)
            # 计算前一道题的题目序号
            previous_topic_number -= 1
            # 更新待查找的文本
            search_text = remaining_text

    # 返回所有答案的列表
    return refined_answers


ANSWERS_KEY_WORDS_IN_QUESTIONS = ["标准答案", "试题分析", "答案", "解析", "答", "解"]


def split_text_by_keywords(text: str, keywords: list) -> dict:
    # Create the regular expression pattern for the first match from the left
    # pattern = r"(【(?:" + "|".join(re.escape(keyword) for keyword in ANSWERS_KEY_WORDS_IN_QUESTIONS) + r")】)"
    pattern = r"【[^】]*】"
    match = re.search(pattern, text)

    if not match:
        pattern = f"({'|'.join(ANSWERS_KEY_WORDS_IN_QUESTIONS)})"
        lines = text.splitlines()

        for index in range(1, len(lines)-1):
            line = lines[index]
            match = re.search(pattern, line)
            if match:
                return {
                    "question": "\n".join(lines[:index]),
                    "answer": "\n".join(lines[index:])
                }
                    
    else:
        # Get the matched text
        matched_text = match.group(0)

        # Split the text into two parts at the matched text
        first_part, second_part = text.split(matched_text, 1)

        # Return the result as a dictionary
        return {
            "question": first_part.strip(),
            "answer": matched_text + second_part.strip()
        }
    


def align_answers_in_questions(questions: list, keywords: list = ANSWERS_KEY_WORDS_IN_QUESTIONS) -> list:
    answers_with_questions = []
    for question in questions:
        answer_with_question = split_text_by_keywords(question, keywords)
        if answer_with_question:
            answers_with_questions.append(answer_with_question)

    return answers_with_questions


def type_of_judgment(text):
    """判断文本类型。

    该函数接受一个文本块，并根据问题编号列表中数字 "1" 的出现情况来确定判断类型。函数假设文本以 "一、"、"二、" 等形式进行编号。

    参数：
        text (str)：包含问题及其编号的输入文本。

    返回：
        bool：如果数字 "1" 出现次数超过问题数量的一半，则返回 True，否则返回 False。
    """
    
    # 将文本拆分成行
    lines = text.splitlines()
    print(lines)
    # 初始化一个空列表用于存储问题编号
    question_number_list = []
    
    # 定义一个正则表达式模式，用于匹配问题编号如 "一、"、"二、" 等
    pattern = r'^[一二三四五六七八九十][、．.]'
    
    # 遍历文本中的每一行
    for i in range(len(lines)):
        line = lines[i]
        
        # 检查当前行是否匹配问题编号的模式
        match = re.match(pattern, line)
        
        if match:
            # 如果匹配成功，从下一行中提取并组合数字，并将其添加到列表中
            if i + 1 < len(lines):
                next_line = lines[i+1]
                question_number_list.append(extract_and_combine_numbers(next_line))
    
    # 统计问题编号列表中数字 "1" 的出现次数
    count_of_ones = question_number_list.count(1)

    # 如果数字 "1" 出现次数超过问题数量的一半，则返回 True，否则返回 False
    return count_of_ones >= len(question_number_list) / 2


def split_question(question, topic_number=0, target_topic_number=0):
    """
    将问题拆分成子问题的函数。

    该函数将给定问题拆分为多个子问题，并返回一个子问题的列表。每个子问题以特定编号开始，编号从 `topic_number` 开始。
    搜索将从 `target_topic_number` 结束。如果未指定 `topic_number` 和 `target_topic_number`，则默认值为0。

    Args:
        question (str): 要拆分的问题文本。
        topic_number (int, optional): 子问题的起始编号。默认值为0。
        target_topic_number (int, optional): 拆分的终止编号。默认值为0。

    Returns:
        list: 包含拆分后的子问题的列表。
    """
    # 如果未指定 topic_number，则从问题文本中提取并组合数字作为起始编号
    topic_number = topic_number if topic_number else extract_and_combine_numbers_in_not_start(question)
    
    # 如果未指定 target_topic_number，则默认情况下进行递归搜索直到结束
    recursion = False if target_topic_number else True
    target_topic_number = target_topic_number if target_topic_number else topic_number + 1

    # 初始化用于存储拆分后子问题的列表
    split_question_list = []
    
    # 从问题文本和起始编号开始搜索子问题
    search_question = question
    search_number = topic_number + 1
    
    # 循环搜索子问题，直到达到目标编号或无法找到更多子问题
    while True:
        # 使用函数 match_specific_from_start 在搜索文本中匹配特定编号的子问题
        current_question, next_question = match_specific_from_start(search_question, search_number)
        
        # 如果找到子问题，将其添加到拆分后的子问题列表中，并更新搜索文本为下一个问题的起始位置
        if current_question is not None:
            split_question_list.append(current_question)
            search_question = next_question
        else:
            break
            
        # 如果已经达到目标编号，而且不需要进行递归搜索，停止拆分
        if target_topic_number - search_number <= 0:
            if not recursion:
                break

        # 增加搜索编号，以搜索下一个子问题
        search_number = search_number + 1
        
    # 将最后一个子问题添加到列表中
    split_question_list.append(search_question)
   
    # 返回拆分后的子问题列表
    return split_question_list


def find_continuous_sequence(all_question):
    """
    查找连续编号问题序列的函数。

    该函数处理给定的问题列表 `all_question`，并查找其中连续编号的问题序列。
    连续编号的问题序列指的是问题编号相邻且连续的问题组成的序列。

    Args:
        all_question (list): 包含问题文本的列表。

    Returns:
        list: 包含连续编号问题序列的列表。
    """
    # 初始化一个新的问题列表，用于存储连续编号问题序列
    new_all_question = []
    
    # 遍历所有问题
    for index, question in enumerate(all_question):
        # 检查是否到达问题列表的末尾
        if index + 1 == len(all_question):
            # 如果到达末尾，则将当前问题拆分后添加到新的问题列表中，然后跳出循环
            new_all_question.append(question)
            break
            
        # 提取当前问题的编号
        topic_number = extract_and_combine_numbers(question)
        
        # 提取下一个问题的编号
        next_topic_number = extract_and_combine_numbers(all_question[index+1])
        
        # 如果当前问题编号加1等于下一个问题编号，则它们是连续的
        if topic_number + 1 == next_topic_number:
            # 将当前问题添加到新的问题列表中
            new_all_question.append(question)
            continue
        
        # 如果当前问题编号和下一个问题编号不连续，则需要拆分当前问题，并将拆分后的子问题添加到新的问题列表中
        new_all_question += split_question(question, topic_number, next_topic_number-1)
        
    # 返回包含连续编号问题序列的新问题列表
    return new_all_question
