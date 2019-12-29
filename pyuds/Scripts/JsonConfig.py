# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 20:15:56 2019

@author: levy.he
"""
import json
import importlib
from .BaseType import ComBase, BusBase, TpBase, DiagClientBase, BaseDiagnostic, Message, DBPaser, TesterBase
from .SecurityKey import BaseKeyGen

BASICCLASS = {'Can': ('CanBus', 'ComCan', 'CanTp'),
              'CanFd': ('CanFdBus', 'ComCanFd', 'CanFdTp'),
              'Fr': ('FrBus', 'ComFr', 'FrTp')}
MSGCLASS = {"Can": {"Tx": ("CanMsgSendOnce", "CanMsgSender"), "Rx": ("CanMsgReadOnce", "CanMsgReader")},
            "DB": {"Tx": ("DBMsgSendOnce", "DBMsgSender"), "Rx": ("DBMsgReadOnce", "DBMsgReader")},
            "Fr": {"Tx": ("FrSendOnce", "FrSender", "FrTimeSender"), "Rx": ("FrReadOnce", "FrReader")}}

def _get_pyuds_class(class_name):

    try:
        module = importlib.import_module("__main__")
        m_class = getattr(module, class_name)
        
    except:
        try:
            module = importlib.import_module("pyuds.PyUds")
            m_class = getattr(module, class_name)
        except:
            raise ImportError(
                "Cannot import {} form {} or {}".format(class_name, "__main__", "PyUds"))
    return m_class


def _get_scripts_class(class_name):

    try:
        module = importlib.import_module("pyuds.Scripts")
    except:
        raise ImportError("Cannot import module Scripts")

    # Get the correct class
    try:
        m_class = getattr(module, class_name)
    except:
        raise ImportError(
            "Cannot import class {} from module {}."
            .format(m_class, "Scripts")
        )
    return m_class

def _get_tester_class(class_name):

    try:
        module = importlib.import_module("__main__")
        m_class = getattr(module, class_name)
    except:
        try:
            module = importlib.import_module("pyuds.TestCase")
            m_class = getattr(module, class_name)
        except:
            raise ImportError(
                "Cannot import {} form {} or {}".format(class_name, "__main__", "TestCase"))
    return m_class

class PyUdsClass(object):
    @staticmethod
    def __new__(cls, class_name, **config):
        cls = _get_pyuds_class(class_name)
        return cls(**config)


class PyUdsClient(DiagClientBase):
    @staticmethod
    def __new__(cls, class_name, tp_protocol, ** config):
        cls = _get_pyuds_class(class_name)
        return cls(tp_protocol=tp_protocol, **config)


class PyUdsDiag(BaseDiagnostic):
    @staticmethod
    def __new__(cls, class_name, buf=[], uds_client=None):
        cls = _get_pyuds_class(class_name)
        return cls(buf=buf, uds_client=uds_client)

class PyUdsCom(ComBase):
    @staticmethod
    def __new__(cls, class_name, **config):
        cls = _get_pyuds_class(class_name)
        return cls(**config)


class PyUdsBus(BusBase):
    @staticmethod
    def __new__(cls, class_name, **config):
        cls = _get_pyuds_class(class_name)
        return cls(**config)


class PyUdsTp(TpBase):
    @staticmethod
    def __new__(cls, class_name, **config):
        cls = _get_pyuds_class(class_name)
        return cls(**config)


class PyKeyGen(BaseKeyGen):
    @staticmethod
    def __new__(cls, class_name, *args, **config):
        cls = _get_scripts_class(class_name)
        return cls(*args, **config)


class PyTester(TesterBase):
    @staticmethod
    def __new__(cls, class_name, client, keygen):
        cls = _get_tester_class(class_name)
        return cls(client, keygen)

class PyMessage(Message):
    @staticmethod
    def __new__(cls, class_name, *args, **kwars):
        cls = _get_pyuds_class(class_name)
        return cls(*args, **kwars)


class PyDBPaser(DBPaser):
    @staticmethod
    def __new__(cls, class_name, *args, **kwars):
        cls = _get_pyuds_class(class_name)
        return cls(*args, **kwars)

class ParamConfigureError(Exception):
    pass


class UdsConfigParse(object):

    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            self.config = json.load(f)
        self._parse_json_value(self.config)
        self.bus_list = []
        self.uds_list = []
        self.msg_list = []

    def GetBus(self, name, start=False):
        if name == 'None':
            return None
        bus = self._get_bus(name,start=start)
        if bus is not None:
            return bus['Bus']
        else:
            raise ParamConfigureError(
                'bus name or bustype configure error[%s]' % (name))

    def GetKeyGens(self, name):
        for i in self.config['Security']:
            if i['Name'] == name:
                gens = []
                for j in i['KeyGens']:
                    if j['Type'] == 'DLL':
                        gen = PyKeyGen('DllKeyGen', *j['Level'], dll_path=j['Param'])
                    elif j['Type'] == 'Class':
                        gen = PyKeyGen(j['Param'], *j['Level'])
                    else:
                        raise ParamConfigureError(
                            'Security key genstype configure error[%s]' % (j['Type']))
                    gens.append(gen)
                return PyKeyGen('SecurityKeyGens',*gens)
        return None

    def GetMsgTester(self, name):
        for i in self.config['UdsTester']:
            if i['Name'] == name:
                if 'Message' in i.keys():
                    msg_ist = {}
                    for msg_name in i['Message']:
                        msg = self.GetMessage(msg_name)
                        msg_ist[msg_name] = msg
                    return msg_ist

    def GetUdsTester(self, name, config_msg=False):
        for i in self.config['UdsTester']:
            if i['Name'] == name:
                uds = self.GetUdsDiag(i['ClientName'])
                key = self.GetKeyGens(i['Security'])
                if config_msg == True and 'Message' in i.keys():
                    for name in i['Message']:
                        msg = self.GetMessage(name)
                        msg.start()
                cls_name = i['Class']
                return PyTester(cls_name, uds, key)
        return None

    def GetUdsDiag(self, name, diag_cls=None):
        uds = self._get_uds_client(name)
        if uds is not None:
            diag_cls = diag_cls if diag_cls is not None else uds['diag_cls']
            diag = PyUdsDiag(diag_cls, uds_client=uds['Uds'])
            return diag
        else:
            raise ParamConfigureError(
                'uds name or bustype configure error[%s]' % (name))

    def GetUdsClient(self, name):
        uds = self._get_uds_client(name)
        if uds is not None:
            return uds['Uds']
        else:
            raise ParamConfigureError(
                'uds name or bustype configure error[%s]' % (name))

    def GetMessage(self, name):
        msg = self._get_message(name)
        if msg is not None:
            return msg['Msg']
        else:
            raise ParamConfigureError(
                'message name or bustype configure error[%s]' % (name))

    def _get_message(self, name):
        for i in self.msg_list:
            if name == i['Name']:
                return i
        for i in self.config['Message']:
            if i['Name'] == name:
                bus = self.GetBus(i['BusName'])
                if i['Type'] == 'DB':
                    db_paser = PyDBPaser('DBPaser', db_path=i['DB_Path'])
                    db_name = i['Name']
                    if 'DBName' in i.keys():
                        db_name = i['DBName']
                    db_msg = db_paser.get_db_msg(db_name)
                    if 'Dir' in i.keys():
                        Dir = i['Dir']
                    else:
                        Dir = 'Rx'
                    cycle = 1
                    config = {}
                    if 'IsCycle' in i.keys():
                        if self._get_bool_value(i['IsCycle']) == False:
                            cycle = 0
                    if 'CycleTime' in i.keys():
                        db_msg['cycle'] = int(i['CycleTime'] * 1000)
                    if cycle == 0 and Dir == 'Rx' and 'Timeout' in i.keys():
                        config['timeout'] = i['Timeout']
                    if 'Signals' in i.keys():
                        for sig in i['Signals'].keys():
                            db_msg['sig_list'][sig]['value'] = i['Signals'][sig]
                    MSG_CLS = MSGCLASS['DB'][Dir][cycle]
                    msg = PyMessage(MSG_CLS,bus,db_msg,**config)
                elif i['Type'] == 'Can':
                    canid = i['ID']
                    args = []
                    if canid > 0X7FF:
                        ext_id = True
                        msg_id = canid & 0x1FFFFFFF
                    else:
                        ext_id = False
                        msg_id = canid & 0x7FF
                    kwargs = dict(arbitration_id=msg_id, is_extended_id=ext_id)
                    if 'Dir' in i.keys():
                        Dir = i['Dir']
                    else:
                        Dir = 'Rx'
                    cycle = 1
                    if 'IsCycle' in i.keys():
                        if self._get_bool_value(i['IsCycle']) == False:
                            cycle = 0
                    if cycle == 1 and Dir == 'Tx':
                        args.append(i['CycleTime'])
                    if cycle == 0 and i['Dir'] == 'Rx':
                        if 'Timeout' in i.keys():
                            kwargs['timeout'] = i['Timeout']
                        elif 'CycleTime' in i.keys():
                            kwargs['timeout'] = i['CycleTime'] * 2
                    dlc = i.get('DLC', 0)
                    data = i.get('Data', [])
                    if dlc > len(data):
                        data = data + [0x00] * (dlc - len(data))
                    kwargs['data'] = data
                    MSG_CLS = MSGCLASS['Can'][Dir][cycle]
                    msg = PyMessage(MSG_CLS, bus, *args, **kwargs)
                elif i['Type'] == 'Fr':
                    config = {}
                    args = []
                    config['slot_id'] = i['SlotId']
                    config['base_cycle'] = i.get('BaseCycle', 0)
                    config['repetition_cycle'] = i.get('RepetitionCycle', 1)
                    single_shot = i.get('SingleShot', 'True')
                    single_shot = self._get_bool_value(single_shot)
                    Dir = i.get('Dir', 'Rx')
                    config['direction'] = Dir
                    config['single_shot'] = single_shot
                    dlc = i.get('DLC', 0)
                    data = i.get('Data', [])
                    if dlc > len(data):
                        data = data + [0x00] * (dlc - len(data))
                    config['data'] = data
                    IsCycle = True
                    if 'IsCycle' in i:
                        IsCycle = self._get_bool_value(i['IsCycle'])
                    if Dir == 'Tx':
                        cycle = 0
                        if single_shot == False:
                            cycle = 1
                        elif IsCycle == True:
                            args.append(i['CycleTime'])
                            cycle = 2
                    else:
                        if IsCycle:
                            cycle = 1
                        else:
                            cycle = 0
                    MSG_CLS = MSGCLASS['Fr'][Dir][cycle]
                    msg = PyMessage(MSG_CLS, bus, *args, **config)
                msg_dict = dict(Name=name, Type=i['Type'], Msg=msg)
                self.msg_list.append(msg_dict)
                return msg_dict

    def _get_uds_client(self, name):
        for i in self.uds_list:
            if name == i['Name']:
                return i
        for i in self.config['UdsClient']:
            if i['Name'] == name:
                bus = self._get_bus(i['BusName'])
                TpCls = BASICCLASS[bus['BusType']][2]
                tp = PyUdsTp(TpCls, **i['TpConfig'])
                Uds = PyUdsClient('DiagClient', tp, **i['DiagConfig'])
                diag_cls = i.get('Class', 'BaseDiagnostic')
                bus['Bus'].add_sender(tp.sender)
                bus['Bus'].add_reader(tp.reader)
                if bus['BusType'] == 'Fr':
                    bus['Bus'].add_fr_cycle_setter(tp.update_fr_cycle)
                uds_dict = {"Name": name, "Uds": Uds,
                            "Bus": bus, "diag_cls": diag_cls}
                self.bus_list.append(uds_dict)
                return uds_dict
        return None


    def _get_bus(self, name, start=False):
        for i in self.bus_list:
            if name == i['Name']:
                return i
        for i in self.config['Bus']:
            if i['Name'] == name:
                busCls = BASICCLASS[i['BusType']][0]
                bus = PyUdsBus(busCls, **i['BusConfig'])
                ComCls = BASICCLASS[i['BusType']][1]
                com_config = i.get('ComConfig',{})
                com = PyUdsCom(ComCls, bus=bus, **com_config)
                if start:
                    com.start()
                bus_dict = {"Name": name, "BusType": i['BusType'], "Bus": com}
                self.bus_list.append(bus_dict)
                return bus_dict
        return None

    def _parse_json_value(self, json):
        if type(json) is dict:
            for key in json.keys():
                json[key] = self._parse_json_value(json[key])
            return json
        elif type(json) is list:
            for i in range(len(json)):
                json[i] = self._parse_json_value(json[i])
            return json
        elif type(json) is str:
            vl = self._try_to_value(json)
            if vl is None:
                vl = json
            return vl
        else:
            return json

    def _get_bool_value(self, s):
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
        else:
            raise ValueError('unknwon bool value %s'%(s))

    def _try_to_value(self, s):
        try:
            s = s.strip()
            if s[:2].lower() == '0x':
                return int(s, 16)
            return int(s)
        except:
            try:
                s = s.strip()
                value = float(s)
                return value
            except:
                return None

if __name__ == '__main__':
    config = UdsConfigParse('UdsConfig.json')
    print(config.config)
