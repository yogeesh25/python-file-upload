import pandas as pd
import numpy as np

class FileValidator(object):

    def __init__(self,data):
 
        self.file = data.get('file')
        self.file_name = data.get('file_name')
        self.headers_list = data.get('headers_list')
        self.validate_for = data.get('validate_for')
        self.file_number = data.get('count')
        self.directory = data.get('failed_directory')
        self.error_file_name = data.get('error_file_name')
        self.is_excel = False
        self.columns = data.get('columns')
        self.extenstion = data.get('extenstion')

    def case_insensitive(self):
        self.df.columns = self.df.columns.str.lower()

    def read_and_validate_file(self):
        if(self.file_name.endswith('.xlsx') or self.file_name.endswith('.xls')):
            self.df = pd.read_excel(self.file)
            self.is_excel = True
        else:
            self.df = pd.read_csv(self.file)
        self.case_insensitive()
        self.updated_df = self.df.replace('nan', np.nan, regex=True).replace('',np.nan,regex=True)
        self.validate_file()
        return self.error_list

    def validate_row(self):
        self.sheet_name = "column_error"
        self.error_filename = f"failed_column_{self.file_name}"
  
        for index,row in self.updated_df.iterrows():
            for j,v in enumerate(row):
                if len(self.error_list):
                    break
                if pd.isna(v):
                    self.error_list = {'row':index,'column name':self.updated_df.columns[j],'message':'value is missing'} 
        self.erron_in = 'column'

    def validate_header(self):
        excel_headers = self.df.columns.tolist()
        improper_list = [{'column name':i,'message':'header is not proper'} for i, j in zip(self.columns, excel_headers) if i != j]
        not_valid_list = [ {'column name':header,'message':'not valid header '} for header in list(set(excel_headers).difference(self.columns))]
        self.error_list = improper_list + not_valid_list
        self.error_list = [dict(t) for t in {tuple(d.items()) for d in self.error_list}]
        for err in self.error_list:
            if 'unnamed' in err['column name']:
                err['column name'] = None
        self.error_list = [err for err in  self.error_list if err['column name']]
        self.error_filename = f"failed_header_{self.file_name}"
        self.sheet_name = "header_error"
        self.erron_in='header'

    def drop_column(self):
        for column in self.updated_df.columns:
            if not self.updated_df[column].isnull().any():
                self.updated_df = self.updated_df.drop([column],axis=1)

    def validate_file(self):
        self.error_list = []
        self.drop_column()
        self.validate_header()
        if len(self.error_list) is 0:
            self.validate_row()


       
