from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from MBTI.models import Question, Answer, Dimension, CodePoint
import pandas as pd

class Command(BaseCommand):
    help = 'Imports data from an Excel file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=str, default=r'C:\Users\Kanjana\ProjectMbti\question_new.xlsx', help='The Excel file path.')

    def handle(self, *args, **options):
        file_path = options['file']

        try:
            # ดำเนินการการนำเข้าข้อมูลสำหรับ Dimension
            #df_dimensions = pd.read_excel(file_path, sheet_name='Dimension')
            #for _, row in df_dimensions.iterrows():
            #    Dimension.objects.get_or_create(
            #        letter=row['letter'],
            #        name=row['name'],
            #        defaults={'detail_en': row['detail_en'], 'detail_th': row['detail_th']}
            #    )
            #self.stdout.write(self.style.SUCCESS('Successfully imported Dimension data'))

            # ดำเนินการการนำเข้าข้อมูลสำหรับ Question
            #df_questions = pd.read_excel(file_path, sheet_name='Question')
            #for _, row in df_questions.iterrows():
            #    Question.objects.create(
            #        text=row['text'])
                
            #self.stdout.write(self.style.SUCCESS('Successfully imported Question data'))

            # ดำเนินการการนำเข้าข้อมูลสำหรับ Answer
            #df_answers = pd.read_excel(file_path, sheet_name='Answer')
            #for _, row in df_answers.iterrows():
            #    question_id = row['question']  # สมมติว่าคอลัมน์นี้เก็บค่า ID ของคำถามจากแผ่น 'Question'
            #    question = Question.objects.get(id=question_id)  # ใช้ get เพื่อค้นหาคำถามโดยใช้ ID
            #    Answer.objects.get_or_create(
            #        question=question,
            #        code=row['code'],
            #        text=row['text']
            #    )
            #self.stdout.write(self.style.SUCCESS('Successfully imported Answer data'))

            # ดำเนินการการนำเข้าข้อมูลสำหรับ CodePoint
            df_codepoints = pd.read_excel(file_path, sheet_name='CodePoint')
            for _, row in df_codepoints.iterrows():
                # หา Dimension โดยใช้ letter จากแผ่น 'Dimension'
                dimension, created = Dimension.objects.get_or_create(letter=row['dimension'])
                CodePoint.objects.get_or_create(
                    code=row['code'],
                    dimension=dimension,
                    defaults={'point': row['point']}
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported CodePoint data'))


        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'IntegrityError occurred: {e}'))
        except Exception as e:
            raise CommandError(f'Error occurred while importing data: {e}')

        self.stdout.write(self.style.SUCCESS('Successfully imported all data from the Excel file.'))

