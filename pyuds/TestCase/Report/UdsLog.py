# -*- coding: utf-8 -*-
"""
Created on Fri May 5 20:13:59 2019

@author: levy.he
"""

import time
import os
import importlib
import importlib.util
from functools import wraps
from .Report import html_report

def list_to_hex_str(data):
    return ' '.join(['%02X'%(x) for x in data])

class UdsNegativeResponse(Exception):
    pass

class UdsNoneResponse(Exception):
    pass

class UdsLoging(object):
    test_step = []
    sub_step = []
    test_case = []
    test_suite = []
    test_group = []
    test_result = []
    requirement = []
    has_sub_test = False
    diag = None
    uu_count = 0
    uu_base = '1281717881'

    def __init__(self, test_level=0, func_request=False, test_type=2, verbose=True, skipped=False):
        '''
        @test_level to indication which log function to use
            0 base uds test step
            1 the test has more than one uds test step
            2 to assert the test response result
            3 the test case that contain test step and test result
            4 the suite of the test case
            5 the group of the test suite
        @test_type indication the test type
            0 only description, not actual step
            1 wait 
            2 diagnostic test
            3 Can Message or FlexRay Frame
            4 requirement
        '''
        self.verbose = verbose
        self.test_type = test_type
        self.level = test_level
        self.func_request = func_request
        self.skipped = skipped

    def __call__(self, func):
        
        @wraps(func)
        def caller(*args, **kwargs):
            resp = None
            UdsLoging.uu_count += 4
            if self.level < 2 and self.test_type==2:
                if hasattr(args[0], 'diag'):
                    self.diag = args[0].diag
                else:
                    self.diag = UdsLoging.diag
                if self.diag is None:
                    raise ValueError(
                        'diag value shall not None, before used for loging')
            if self.level == 0:
                resp = self.base_test_log(caller, func, *args, **kwargs)
            elif self.level == 1:
                resp = self.sub_step_test_log(caller, func, *args, **kwargs)
            elif self.level == 2:
                resp = self.test_assert_log(caller, func, *args, **kwargs)
            elif self.level == 3:
                if not self.skipped:
                    resp = self.test_case_log(caller, func, *args, **kwargs)
            elif self.level == 4:
                if not self.skipped:
                    UdsLoging.collect_test_case()
                    UdsLoging.uu_count += 4
                    resp = self.test_suite_log(caller, func, *args, **kwargs)
            elif self.level == 5:
                if not self.skipped:
                    UdsLoging.collect_test_case()
                    UdsLoging.uu_count += 4
                    resp = self.test_group_log(caller, func, *args, **kwargs)
            return resp
        return caller

    @staticmethod
    def get_all_result():
        UdsLoging.collect_test_case()
        total = sum([x['result'][0] for x in UdsLoging.test_group])
        passed = sum([x['result'][1] for x in UdsLoging.test_group])
        failed = sum([x['result'][2] for x in UdsLoging.test_group])
        error = sum([x['result'][3] for x in UdsLoging.test_group])
        return total, passed, failed, error

    @staticmethod
    def collect_test_case():
        '''used to collect the test case that not reocord by uds log
           this is usefull to log the test case that not run in test suite or test group 
        '''
        if UdsLoging.test_case:
            UdsLoging.uu_count += 4
            uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
            start_time = UdsLoging.test_case[0]['start_time']
            end_time = UdsLoging.test_case[-1]['end_time']
            step_count = len(UdsLoging.test_suite) + 1
            step_desc = 'TestSuite_%d_NoName' % (step_count) 
            total = len(UdsLoging.test_case)
            passed = len([x for x in UdsLoging.test_case if x['test_result']['result'] == 'Pass'])
            failed = len([x for x in UdsLoging.test_case if x['test_result']['result'] == 'Failed'])
            error = len([x for x in UdsLoging.test_case if x['test_result']['result'] == 'Error'])
            test_desc = dict(uid=uid, result=(total, passed, failed, error),
                step_desc=step_desc, test_case=UdsLoging.test_case, start_time=start_time, end_time=end_time, step_count=step_count)
            UdsLoging.test_suite.append(test_desc)
            UdsLoging.test_case = []

        if UdsLoging.test_suite:
            UdsLoging.uu_count += 4
            uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
            start_time = UdsLoging.test_suite[0]['start_time']
            end_time = UdsLoging.test_suite[-1]['end_time']
            step_count = len(UdsLoging.test_group) + 1
            step_desc = 'TestGroup_%d-NoName' % (step_count) 
            total = sum([x['result'][0] for x in UdsLoging.test_suite])
            passed = sum([x['result'][1] for x in UdsLoging.test_suite])
            failed = sum([x['result'][2] for x in UdsLoging.test_suite])
            error = sum([x['result'][3] for x in UdsLoging.test_suite])
            test_desc = dict(uid=uid, step_desc=step_desc, result=(total, passed, failed, error),
                 test_suite=UdsLoging.test_suite, start_time=start_time, end_time=end_time, step_count=step_count)
            UdsLoging.test_group.append(test_desc)
            UdsLoging.test_suite = []            

    def test_group_log(self, caller, func, *args, **kwargs):
        uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        UdsLoging.test_suite = []
        start_time = time.time()
        resp = func(*args, **kwargs)
        end_time = time.time()
        step_count = len(UdsLoging.test_group) + 1
        if hasattr(caller, 'desc'):
            step_desc = caller.desc
            del caller.desc
        elif 'desc' in kwargs.keys():
            step_desc = kwargs['desc']
        else:
            step_desc = 'TestGroup_%d-' % (step_count) + func.__name__
        total = sum([x['result'][0] for x in UdsLoging.test_suite])
        passed = sum([x['result'][1] for x in UdsLoging.test_suite])
        failed = sum([x['result'][2] for x in UdsLoging.test_suite])
        error = sum([x['result'][3] for x in UdsLoging.test_suite])
        test_desc = dict(uid=uid, step_desc=step_desc, result=(total, passed, failed, error),
             test_suite=UdsLoging.test_suite, start_time=start_time, end_time=end_time, step_count=step_count)
        UdsLoging.test_group.append(test_desc)
        UdsLoging.test_suite = []
        return resp

    def test_suite_log(self, caller, func, *args, **kwargs):
        uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        UdsLoging.test_case = []
        start_time = time.time()
        resp = func(*args, **kwargs)
        end_time = time.time()
        step_count = len(UdsLoging.test_suite) + 1
        if hasattr(caller, 'desc'):
            step_desc = caller.desc
            del caller.desc
        elif 'desc' in kwargs.keys():
            step_desc = kwargs['desc']
        else:
            if hasattr(func, '__self__'):
                step_desc = 'TestSuite_%d-' % (step_count) + func.__self__.__class__.__name__
            else :
                step_desc = 'TestSuite_%d-' % (step_count) + func.__name__
        test_case = [x for x in UdsLoging.test_case if x['test_result'] is not None]
        total = len(test_case)
        passed = len([x for x in test_case if x['test_result']['result'] == 'Pass'])
        failed = len([x for x in test_case if x['test_result']['result'] == 'Failed'])
        error = len([x for x in test_case if x['test_result']['result'] == 'Error'])
        test_desc = dict(uid=uid, result=(total, passed, failed, error),
            step_desc=step_desc, test_case=UdsLoging.test_case, start_time=start_time, end_time=end_time, step_count=step_count)
        UdsLoging.test_suite.append(test_desc)
        UdsLoging.test_case = []
        return resp

    def test_case_log(self, caller, func, *args, **kwargs):
        uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        UdsLoging.test_step = []
        UdsLoging.test_result = []
        UdsLoging.requirement = []
        start_time = time.time()
        try:
            resp = func(*args, **kwargs)
        except UdsNegativeResponse as ex:
            step_count = len(UdsLoging.test_step) + 1
            UdsLoging.test_result.append(dict(result='Error', step_desc=str(ex), requirement=UdsLoging.requirement,
             step_count=step_count, start_time=start_time, end_time=time.time()))
            resp = None
        except UdsNoneResponse as ex:
            step_count = len(UdsLoging.test_step) + 1
            UdsLoging.test_result.append(dict(result='Error', step_desc=str(ex), requirement=UdsLoging.requirement,
            step_count=step_count, start_time=start_time, end_time=time.time()))
            resp = None
        if len(UdsLoging.test_result) == 0:
            UdsLoging.test_result.append(None)

        if hasattr(caller, 'desc'):
            caller_desc = caller.desc
            del caller.desc
        elif 'desc' in kwargs.keys():
            caller_desc = kwargs['desc']
        else:
            caller_desc = func.__name__

        last_step = 0
        for count, result in enumerate(UdsLoging.test_result, start=1):
            step_count = len(UdsLoging.test_case) + 1
            if result is not None:
                end_time = result['end_time']
                step_desc = '{}_{}'.format(caller_desc, count)
                current_step = result['step_count'] - 1
                if self.verbose:
                    print('%d.%d-%s:%s' % (len(UdsLoging.test_suite) + 1, step_count, step_desc, result['result']))
                test_step = UdsLoging.test_step[last_step:current_step]
                requirement = result.get('requirement', ['NA'])
                test_desc = dict(test_result=result, uid=uid, requirement=requirement, 
                                 step_desc=step_desc, test_step=test_step, start_time=start_time, end_time=end_time, step_count=step_count)
                start_time = end_time
                last_step = current_step
            else:
                end_time = UdsLoging.test_step[-1]['end_time']
                step_desc = '{}_{}'.format(caller_desc, count)
                if self.verbose:
                    print('%d.%d-%s:%s' % (len(UdsLoging.test_suite) + 1, step_count, step_desc, "None"))
                test_step = UdsLoging.test_step[last_step:]
                test_desc = dict(test_result=None, uid=uid, requirement=[], 
                                 step_desc=step_desc, test_step=test_step, start_time=start_time, end_time=end_time, step_count=step_count)
            UdsLoging.test_case.append(test_desc)
            UdsLoging.uu_count += 4
            uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        UdsLoging.test_step = []
        UdsLoging.test_result = []
        UdsLoging.requirement = []
        return resp

    def test_assert_log(self, caller, func, *args, **kwargs):
        uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        start_time = time.time()
        resp = func(*args, **kwargs)
        end_time = time.time()
        step_count = len(UdsLoging.test_step) + 1
        if hasattr(caller, 'desc'):
            step_desc = caller.desc
            del caller.desc
        elif 'desc' in kwargs.keys():
            step_desc = kwargs['desc']
        else:
            step_desc = 'TestAssert_%d' % (step_count)
        if resp is not None :
            result = 'Pass' if resp else 'Failed'
        else:
            result = 'Error'
        if hasattr(caller, 'expect'):
            expect = caller.expect
            del caller.expect
        else:
            expect = None
        if hasattr(caller, 'actual'):
            actual = caller.actual
            del caller.actual
        else:
            actual = None

        test_desc = dict(result=result, expect=expect, actual=actual, uid=uid, requirement=UdsLoging.requirement,
            step_desc=step_desc, start_time=start_time, end_time=end_time, step_count=step_count)
        UdsLoging.test_result.append(test_desc)
        UdsLoging.requirement=[]
        return resp

    def sub_step_test_log(self, caller, func, *args, **kwargs):
        uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        UdsLoging.has_sub_test = True
        UdsLoging.sub_step = []
        start_time = time.time()
        resp = func(*args, **kwargs)
        end_time = time.time()
        step_count = len(UdsLoging.test_step) + 1
        if hasattr(caller, 'desc'):
            step_desc = caller.desc
            del caller.desc
        elif 'desc' in kwargs.keys():
            step_desc = kwargs['desc']
        else:
            step_desc = 'TestSubStep_%d' % (step_count)
        step = UdsLoging.test_step
        test_desc = dict(uid=uid,
            step_desc=step_desc, sub_step=UdsLoging.sub_step, start_time=start_time, end_time=end_time, step_count=step_count)
        step.append(test_desc)
        UdsLoging.has_sub_test = False
        UdsLoging.sub_step = []
        if hasattr(caller, 'IsCheck'):
            if caller.IsCheck is True:
                self._resp_process(resp)
            del caller.IsCheck
        return resp

    def base_test_log(self, caller, func, *args, **kwargs):
        uid = UdsLoging.uu_base+'_%04d' % (UdsLoging.uu_count)
        start_time = time.time()
        resp = func(*args, **kwargs)
        end_time = time.time()
        if self.test_type == 4:
            #requirement type
            if hasattr(caller, 'desc'):
                UdsLoging.requirement.append(caller.desc)
            return resp
        else:
            if UdsLoging.has_sub_test is True:
                step_count = len(UdsLoging.sub_step) + 1
                step = UdsLoging.sub_step
            else:
                step_count = len(UdsLoging.test_step) + 1
                step = UdsLoging.test_step
        if hasattr(caller, 'desc'):
            step_desc = caller.desc
            del caller.desc
        elif 'desc' in kwargs.keys():
            step_desc = kwargs['desc']
        else:
            step_desc = 'TestSubStep_%d-' % (step_count) + func.__name__
        if self.test_type == 2:
            req_raw = self.diag.RawValue[:]
            if self.func_request is True:
                req_id = self._get_func_addr_str()
            else:
                req_id = self._get_request_addr_str()
            resp_id = self._get_response_addr_str()
            if resp is not None:
                resp_raw = resp.RawValue[:]
            else:
                resp_raw = None
            
            test_desc = dict(req_raw=req_raw, resp_raw=resp_raw, req_id=req_id, resp_id=resp_id, result=True, uid=uid, test_type=self.test_type,
                             step_desc=step_desc, start_time=start_time, end_time=end_time, step_count=step_count)
            step.append(test_desc)
            if hasattr(caller, 'IsCheck'):
                if caller.IsCheck is True:
                    self._resp_process(resp)
                del caller.IsCheck
        elif self.test_type in [0, 1]:
            test_desc = dict(result=True, uid=uid, test_type=self.test_type,
                             step_desc=step_desc, start_time=start_time, end_time=end_time, step_count=step_count)
            step.append(test_desc)
        elif self.test_type == 3:
            msg = resp
            if msg is not None:
                cls_list = [x.__name__ for x in msg.__class__.__mro__]
                if 'FrFrame' in cls_list:
                    msg = 'FrFrame', msg.slot_id, msg.cycle, msg.direction, len(msg.data), msg.data[:]
                elif 'Message' in cls_list:
                    if msg.is_extended_id:
                        id_str = "ID: {0:08X}".format(msg.arbitration_id)
                    else:
                        id_str = "ID: {0:04X}".format(msg.arbitration_id)
                    msg = 'Can', id_str, msg.direction, len(msg.data), msg.data[:]

            test_desc = dict(result=True, uid=uid, test_type=self.test_type, msg=msg,
                             step_desc=step_desc, start_time=start_time, end_time=end_time, step_count=step_count)
            step.append(test_desc)
        else:
            test_desc = dict(result=True, uid=uid, test_type=self.test_type,
                             step_desc=step_desc, start_time=start_time, end_time=end_time, step_count=step_count)
            step.append(test_desc)
        return resp

    def _get_request_addr_str(self):
        name = self.diag.getTpName()
        addr = self.diag.getTpAddrInfo()[0]
        if name in ['CanTp', 'CanFdTp']:
            ext = ''
            if addr > 0x7FF:
                ext = 'x'
            return '%03X' % (addr) + ext
        elif name == 'FrTp':
            return '%04X' % (addr)
        else:
            return str(addr)

    def _get_func_addr_str(self):
        name = self.diag.getTpName()
        addr = self.diag.getTpAddrInfo()[1]
        if name in ['CanTp', 'CanFdTp']:
            ext = ''
            if addr > 0x7FF:
                ext = 'x'
            return '%03X' % (addr) + ext
        elif name == 'FrTp':
            return '%04X' % (addr)
        else:
            return str(addr)

    def _get_response_addr_str(self):
        name = self.diag.getTpName()
        addr = self.diag.getTpAddrInfo()[2]
        if name in ['CanTp', 'CanFdTp']:
            ext = ''
            if addr > 0x7FF:
                ext = 'x'
            return '%03X' % (addr) + ext
        elif name == 'FrTp':
            return '%04X' % (addr)
        else:
            return str(addr)

    def _resp_process(self, diag_resp):
        if diag_resp is None:
            raise UdsNegativeResponse('Diag Request not response')
        elif not diag_resp.IsPositiveResponse:
            raise UdsNoneResponse(
                'Diag Request negative response[%02X]' % (diag_resp.NRC))

class UdsTestSuite(object):

    @UdsLoging(test_level=4)
    def Run(self):
        this = UdsTestSuite.Run
        this.desc = self.__class__.__name__
        k_list = []
        s_func = None
        e_func = None
        for k, v in self.__class__.__dict__.items():
            if hasattr(v, '__closure__') and v.__closure__ is not None and len(v.__closure__) > 2:
                caller = v.__closure__[2].cell_contents
                if isinstance(caller, UdsLoging) and caller.level == 3:
                    if 'setUpTest' == k:
                        s_func = getattr(self, 'setUpTest')
                    elif 'tearDownTest' == k:
                        e_func = getattr(self, 'tearDownTest')
                    else:
                        k_list.append(k)
        if s_func is not None:
            s_func()
        if e_func is not None:
            e_func()
        for k in k_list:
            func = getattr(self, k)
            func()

class LoadTest(object):
    def __init__(self, path=None, hidden='.'):
        if path is None:
            self.path = '.'
        else:
            self.path = path
        self.hidden = hidden
    
    def get_all_test_file(self, path):
        py_files = []
        for cwd, _, files in os.walk(path):
            for file in files:
                fpath = os.path.join(cwd, file)
                re_file_path = os.path.relpath(fpath, path).replace('\\', ' / ')
                r_list=re_file_path.split('/')
                hide=False
                for rs in r_list:
                    if self.hidden is not None and rs.startswith(self.hidden):
                        hide = True
                if not hide and os.path.isfile(fpath) and os.path.splitext(fpath)[-1].lower() == '.py':
                    fpath = os.path.abspath(fpath)
                    py_files.append(fpath)
        return py_files

    def get_module_from_file(self, file):
        base_name = os.path.basename(file)
        module_name = os.path.splitext(base_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_groups_from_module(self, mod):
        groups = []
        for v in map(lambda x: getattr(mod, x), dir(mod)):
            if hasattr(v, '__closure__') and v.__closure__ is not None and len(v.__closure__) > 2:
                caller = v.__closure__[2].cell_contents
                if isinstance(caller, UdsLoging) and caller.level == 5:
                    groups.append(v)
        return groups

    def load_all_test_group(self):
        py_list = self.get_all_test_file(self.path)
        test_groups = []
        for py in py_list:
            module = self.get_module_from_file(py)
            groups = self.get_groups_from_module(module)
            test_groups += groups
        return test_groups

    def test_report(self, out_path, title, test_info, test_detail):
        start_time = time.time()
        py_list = self.get_all_test_file(self.path)
        current_work_path = os.getcwd()
        for py in py_list:
            module = self.get_module_from_file(py)
            groups = self.get_groups_from_module(module)
            new_work_path = os.path.dirname(module.__file__)
            os.chdir(new_work_path)
            for group in groups:
                group()
        os.chdir(current_work_path)

        test_result = UdsLoging.get_all_result()
        test_list = UdsLoging.test_group
        end_time = time.time()
        report = html_report(out_path)
        report.test_report(test_list, test_result, start_time, end_time,
                           title=title,
                           test_info=test_info,
                           test_detail=test_detail)

