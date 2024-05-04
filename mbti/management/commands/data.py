from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.db import connection
from MBTI.models import Question, Answer, Dimension, CodePoint
import pandas as pd

class Command(BaseCommand):
    help = 'Imports data from an Excel file into the database.' 

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=str, default=r'C:\Users\Mario\ProjectMbti\question_new.xlsx', help='The Excel file path.')

    def handle(self, *args, **options):
        file_path = options['file']
        
        # ลบข้อมูลทั้งหมดจากตาราง Dimension, Question, Answer, และ CodePoint
        Dimension.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        CodePoint.objects.all().delete()

        # ทำการรีเซ็ตค่าไอดีอัตโนมัติ
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='MBTI_dimension'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='MBTI_question'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='MBTI_answer'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='MBTI_codepoint'")


        try:
            # นำเข้าข้อมูล Dimension
            df_dimensions = pd.read_excel(file_path, sheet_name='Dimension')
            for _, row in df_dimensions.iterrows():
                Dimension.objects.get_or_create(
                    letter=row['letter'],
                    name=row['name'],
                    defaults={'detail_en': row['detail_en'], 'detail_th': row['detail_th']}
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported Dimension data'))

            # นำเข้าข้อมูล Question
            df_questions = pd.read_excel(file_path, sheet_name='Question')
            for _, row in df_questions.iterrows():
                Question.objects.create(
                    text=row['text'])
                
            self.stdout.write(self.style.SUCCESS('Successfully imported Question data'))

            # นำเข้าข้อมูล Answer
            df_answers = pd.read_excel(file_path, sheet_name='Answer')
            for _, row in df_answers.iterrows():
                question_id = row['question']  # สมมติว่าคอลัมน์นี้เก็บค่า ID ของคำถามจากแผ่น 'Question'
                question = Question.objects.get(id=question_id)  # ใช้ get เพื่อค้นหาคำถามโดยใช้ ID
                Answer.objects.get_or_create(
                    question=question,
                    code=row['code'],
                    text=row['text']
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported Answer data'))

            # นำเข้าข้อมูล CodePoint
            df_codepoints = pd.read_excel(file_path, sheet_name='CodePoint')
            for _, row in df_codepoints.iterrows():
                dimension_id = row['dimension']
                code_text = row['code']  
                dimension = Dimension.objects.get(id=dimension_id)
                answer = Answer.objects.get(code=code_text)  
                
                CodePoint.objects.create(
                    code=answer,
                    dimension=dimension,
                    point=row['point']
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported CodePoint data'))


        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'IntegrityError occurred: {e}'))
        except Exception as e:
            raise CommandError(f'Error occurred while importing data: {e}')

        self.stdout.write(self.style.SUCCESS('Successfully imported all data from the Excel file.'))

