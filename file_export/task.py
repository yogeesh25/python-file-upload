from file_upload.settings import BASE_DIR
import json
import os
import ast
import numpy as np
import pandas as pd
from datetime import date, time
from celery import shared_task
# from .models import FileUploadManager
from .validating_excel import FileValidator
import tempfile

@shared_task
def file_upload_task(file_path,file_name):
  
    is_excel = False
    headers_list = [
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

    file_count = 1
    chunck_size =  1
    temdir = tempfile.gettempdir()
    extenstion = file_name.split('.')[1]
    df,is_excel = read_file(file_path,file_name)
    query_bundler = query_dict(file_path,file_name,file_count,headers_list)
    get_or_create_dir(query_bundler['successeded_directory'],temdir)
    path = os.path.join(temdir,query_bundler['successeded_directory'])
    if is_excel:
        for chunk in np.array_split(df,len(df) //chunck_size):
            # print(chunk,'chunk')
            print(os.path.join(path, f"{'successeded_file'}_{file_count}.{extenstion}"),'p')
            
            chunk.to_excel(os.path.join(path, f"{'successeded_file'}_{file_count}.{extenstion}"),index=False)
            file_count += 1
    else:
        for chunk in pd.read_csv(file_path,chunksize=chunck_size):
            chunk.to_csv(os.path.join(path, f"{'successeded_file'}_{file_count}.{extenstion}"),index=False)
            file_count += 1
    insert_data_into_db(path,'successeded_file',extenstion)

def query_dict(file_path,file_name,file_count,headers_list):
    query_dict = dict()
    query_dict['file'] = file_path
    query_dict['file_name'] = file_name
    query_dict['count'] = file_count
    query_dict['splitted_dir'] = 'splitted_dir'
    query_dict['failed_directory'] = 'failed_file_folder'
    query_dict['successeded_directory'] = 'successeded_directory'
    query_dict['error_file_name']  = 'failed_file'
    query_dict['successeded_file_name']  = 'successeded_file'
    query_dict['headers_list'] = headers_list
    query_dict['validate_for'] = "column"
    return query_dict

def get_or_create_dir(new_dir,temp_dir):
    
    if not os.path.exists(os.path.join(temp_dir,new_dir)):
        os.makedirs(os.path.join(temp_dir,new_dir))

def read_file(file_path,file_name):
    is_excel = False
    if(file_name.endswith('.xlsx') or file_name.endswith('.xls')):
        df = pd.read_excel(file_path)
        is_excel = True
    else:
        df = pd.read_csv(file_path)
    return df,is_excel
 
def insert_data_into_db(directory_path,file_name,extenstion):
  
    for (dirpath, dirnames, filenames) in os.walk(directory_path):  
        for index,file in enumerate(filenames):
            
            try:
                fl_name = f"{file_name}_{index+1}.{extenstion}"
                path =  os.path.join(directory_path,fl_name)
                df,_ = read_file(path,fl_name)
                
                # for index,row in df.iterrows():
                #     file_manager_instance = FileUploadManager()
                #     file_manager_instance.first_name = row['first name']
                #     file_manager_instance.last_name = row['last name']
                #     file_manager_instance.created_by_id = 1
                #     file_manager_instance.save()
            except Exception as e:
                print('excee',e)
                if os.path.isfile(os.path.join(directory_path,file)):
                    os.remove(os.path.join(directory_path,file))

