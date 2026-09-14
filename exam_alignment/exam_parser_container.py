from .type_exam_parser.abstract_exam_parser import AbstractExamParser

from .type_exam_parser.annotated_exam_parser import AnnotatedExamParser
from .type_exam_parser.standard_exam_parser import StandardExamParser
from .type_exam_parser.split_exam_parser import SplitExamParser

class ExamParserContainer():
    def __init__(self, content):
        self.content = content
        self.parser = self.get_exam_parser()

    def get_exam_parser(self):
        if not AbstractExamParser.check_contains_answers(self.content):
            return None

        if StandardExamParser.detect_this_exam_type(self.content):
            return StandardExamParser(self.content)

        if AnnotatedExamParser.detect_this_exam_type(self.content):
            return AnnotatedExamParser(self.content) 
        
        if SplitExamParser.detect_this_exam_type(self.content):
            return SplitExamParser(self.content) 

        return None
    
    def get_questions(self):
        return self.parser.questions

    def get_answer(self):
        return self.parser.answers
    
    def align(self):
        return self.parser.align()
    