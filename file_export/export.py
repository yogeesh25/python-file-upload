import xlwt
import csv
import pandas as pd
from io import BytesIO, StringIO
from django.http import HttpResponse
from django.utils.encoding import smart_str

def export_to_xls(data,file_name,sheet_name,columns):
    print(columns,'cc',file_name,sheet_name,data)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+file_name

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(sheet_name)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    print(columns,'c--')
    columns = columns

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = data
    for row in rows:
        row_num = row_num + 1
        print(row,'ro')
        ws.write(row_num, 0, row['row'], font_style)
        ws.write(row_num, 1, row['column name'], font_style)
        ws.write(row_num, 2, row['message'], font_style)
        # ws.write(row_num, 3, row.notes, font_style) 

    wb.save(response)
    return response


def export_to_csv(data,file_name,columns):
    print('csv')
    response = HttpResponse(content_type='text/csv')
	#decide the file name
    response['Content-Disposition'] = 'attachment; filename='+file_name

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

	#write the headers
    writer.writerow([
		smart_str(u"row"),
		smart_str(u"column name"),
		smart_str(u"message"),
	])
	#get data from database or from text file....
    events = data #dummy function to fetch data
    for event in events:
        print(events,'eeee')
        writer.writerow([
			smart_str(event['row']),
			smart_str(event['column name']),
			smart_str(event['message'])
		])
    return response


def export_to_excel_by_io(data,sheet_name):
    sio = BytesIO()
    pd_df = pd.DataFrame(data)
    pdwrt = pd.ExcelWriter(sio, engine='xlsxwriter') 
    pd_df.to_excel(pdwrt, sheet_name=sheet_name)
    pdwrt.save()
    sio.seek(0)
    workbook = sio.getvalue()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # set the file name in the Content-Disposition header
    response['Content-Disposition'] = 'attachment; filename=myError.xlsx'
    return response