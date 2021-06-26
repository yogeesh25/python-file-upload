import os
from django.http import response
import pandas as pd 
import numpy as np
from file_upload.settings import BASE_DIR
from rest_framework.views import APIView
from celery import current_app
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication, permissions
from .task import file_upload_task
from .validating_excel import FileValidator
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.authentication import JWTAuthentication
from io import StringIO
from django.http import StreamingHttpResponse
from .export  import *

class FileUploadAPI(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        print('came')
        import time
        start_time = time.time()
        self.file = request.FILES.get('file')
        self.file_name = self.file.name
        self.context = {}
        self.headers_list = [
            {
                'header_name':'first name',
                'required':True
            },
            {
                'header_name':'last name',
                'required':True
            },
            {
                'header_name':'other name',
                'required':False
            }
        ]

        extenstion = self.file_name.split('.')[1]
        columns = [cl['header_name'] for cl in self.headers_list if cl['required']]
        query_bundler = {
            'file':self.file,
            'file_name':self.file_name,
            'headers_list': self.headers_list,
            'extenstion':extenstion,
            'columns':columns   
        }

        file_path =  os.path.abspath(request.FILES['file'].name)
        start_time
        error_list =  FileValidator(query_bundler).read_and_validate_file()
        # end_time = time.time() - start_time
        # print(end_time,'endd')
        # col = ['row','column name','message']
        self.status_code = 200
        self.final_dict = {}
        if len(error_list):
            self.status_code = 400
            self.final_dict = {
                'message':"Error found in excel",
                'detail':"There may be a missing column or misssing values in row of column,please check column and headers of file.",
                "success":False
                }
            # if erron_in == 'column':
            #     if is_excel:
            #         return export_to_xls(error_list,error_filename,sheet_name,col)
            #     return export_to_csv(error_list,error_filename,col)
            # return Response({'data':error_list},status=400)    
        else:
            task = file_upload_task.delay(file_path,self.file_name)
            self.context['task_id'] = task.id
            self.context['task_status'] = task.status
            self.final_dict = self.context
        return Response({'data':self.final_dict},status=self.status_code)

class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            response_data['results'] = task.get()

        return JsonResponse(response_data)