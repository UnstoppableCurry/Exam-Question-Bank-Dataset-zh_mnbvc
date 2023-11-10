from .abstract_exam_parser import AbstractExamParser
import re

class SplitExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)

    @staticmethod
    def detect_this_exam_type(content):
        pass


    def extract_questions(self):
        pass


    def extract_answers(self):
        pass

 
    def align(self):
        pass
