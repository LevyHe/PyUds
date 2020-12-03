# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 16:34:35 2019

@author: levy.he
"""
import xlrd
import os

def try_to_value(s):
    s = s.strip()
    try:
        if s[:2].lower() == '0x':
            return int(s, 16)
        return int(s)
    except:
        try:
            value = float(s)
            return value
        except:
            return None

def try_to_list(s):
    objs = [try_to_value(x) for x in s.split(',')]
    return objs

class ExcelToJson(object):

    def __init__(self, excel_path):
        if not os.path.exists(excel_path):
            raise Exception('%s is not exists' % (excel_path))
        self.excel_path = excel_path
        self.work_book = xlrd.open_workbook(excel_path)

    def __del__(self):
        self.work_book_close()
    
    def work_book_close(self):
        self.work_book.release_resources()

    @staticmethod
    def try_to_value(s):
        s = s.strip()
        try:
            if s[:2].lower() == '0x':
                return int(s, 16)
            return int(s)
        except:
            try:
                value = float(s)
                return value
            except:
                return None

    @staticmethod
    def try_to_list(s):
        objs = [try_to_value(x) for x in s.split(',')]
        return objs

    def GetSheetHeaderCols(self, sheet, *keys, HeaderRowNum=0):
        key_cols = {}
        try:
            header_row = sheet.row_values(HeaderRowNum)
            for key in keys:
                key_cols[key] = header_row.index(key)
            return key_cols
        except:
            raise Exception('%s has error Column name' % (sheet.name))

    def GetSheetJsons(self, sheet_name, *keys, start_row=0):
        sheet = self.work_book.sheet_by_name(sheet_name)
        cols = self.GetSheetHeaderCols(sheet, *keys, HeaderRowNum=start_row)
        row_nums = sheet.nrows
        objs = []
        for i in range(start_row+1, row_nums):
            rows = sheet.row_values(i)
            obj = {}
            for key in cols.keys():
                val = rows[cols[key]]
                if type(val) == float:
                    val = '{0:n}'.format(val)
                else:
                    val = str(val).strip()
                    val = val.strip("'")
                obj[key] = val
            objs.append(obj)
        return objs

    def GetSheetJsonByCols(self, sheet_name, *cols, start_row=0):
        sheet = self.work_book.sheet_by_name(sheet_name)
        row_nums = sheet.nrows
        objs = []
        for i in range(start_row, row_nums):
            rows = sheet.row_values(i)
            obj = {}
            for col in cols:
                val = rows[col]
                if type(val) == float:
                    val = '{0:n}'.format(val)
                else:
                    val = str(val).strip()
                    val = val.strip("'")
                obj[col] = val
            objs.append(obj)
        return objs
    
