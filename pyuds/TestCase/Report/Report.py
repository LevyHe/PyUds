# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 16:10:22 2019

@author: levy.he
"""
from mako.template import Template
from mako import exceptions
import os

class html_report(object):
    
    def __init__(self, out_path, template_path=None):
        self.out_path = out_path
        if template_path is None:
            self.template_path = os.path.join(
                os.path.dirname(__file__), 'r_template.template.html')
        else:
            self.template_path = template_path
        self.template = Template(filename=self.template_path, input_encoding='utf-8', output_encoding='utf-8')

    def test_report(self, groups, test_result, start_time, end_time,
                    title='PyUdsReport',
                    test_detail='no information',
                    test_info='diagnostic test resport'):
        try:
            out_str = self.template.render(
                                            test_groups=groups,
                                            test_result=test_result,
                                            start_time=start_time,
                                            end_time=end_time,
                                            title=title,
                                            test_info=test_info,
                                            test_detail=test_detail
                                           )
            with open(self.out_path, 'wb') as out_fd:
                out_fd.write(out_str)
        except:
            error_str = exceptions.html_error_template().render()
            print('html report error')
            with open('Exception.html', "wb") as errfd:
                errfd.write(error_str)
