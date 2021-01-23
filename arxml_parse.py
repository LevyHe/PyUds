# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 10:18:10 2018

@author: levy.he
"""

import xml.etree.ElementTree as ET
import uuid
ns = "{http://autosar.org/schema/r4.0}"

class ArxmlParse(object):
    ends = '\n'
    #ecu_path='./%sAR-PACKAGES/%sAR-PACKAGE/%sELEMENTS/%sCONTAINERS/%sECUC-CONTAINER-VALUE/%sSUB-CONTAINERS'%(ns,ns,ns,ns,ns,ns,ns)
    def __init__(self,xml_path,max_dids=5):
        ET.register_namespace('', "http://autosar.org/schema/r4.0")
        self.xml_path = xml_path
        self.DDidMaxElements = max_dids
        self.tree=ET.parse(xml_path)
        self.root=self.tree.getroot()
        #self.root[0][0][1][0][4][0][2][3][3]
        self.ecu_list=list(self.root.find('.//%sECUC-CONTAINER-VALUE/[%sSHORT-NAME="DcmDsp"]/%sSUB-CONTAINERS'%(ns,ns,ns)))
    def is_not_dynamically_did(self,didinfo):
        c=didinfo.find('.//%sECUC-NUMERICAL-PARAM-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidDynamicallyDefined"]/%sVALUE'%(ns,ns,ns))
        if c is not None:
            return True if c.text=='false' else False
        else:
            return None
    def GetEcuUUID(self,name=''):
        return uuid.uuid4()
    def get_ecu_func(self,info):
        func_list=[]
        res_text="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataUsePort"
        use_port=info['diddata'].find('./%sPARAMETER-VALUES/%sECUC-TEXTUAL-PARAM-VALUE/[%sDEFINITION-REF="%s"]/%sVALUE'%(ns,ns,ns,res_text,ns))
        if use_port is None:
            return func_list
        if use_port.text=='USE_DATA_SYNCH_FNC':
            sync=True
        else:
            sync=False
        res_text="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataConditionCheckReadFnc"
        func=info['diddata'].find('./%sPARAMETER-VALUES/%sECUC-TEXTUAL-PARAM-VALUE/[%sDEFINITION-REF="%s"]/%sVALUE'%(ns,ns,ns,res_text,ns))
        func_dict={}
        if func is not None:
            func_dict['type']='check'
            func_dict['did']=info['didvalue']
            func_dict['desc']='None'
            func_dict['sync']=sync
            func_dict['func_name']=func.text
            func_list.append(func_dict)
        res_text="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataReadDataLengthFnc"
        func=info['diddata'].find('./%sPARAMETER-VALUES/%sECUC-TEXTUAL-PARAM-VALUE/[%sDEFINITION-REF="%s"]/%sVALUE'%(ns,ns,ns,res_text,ns))
        func_dict={}
        if func is not None:
            func_dict['type']='readlength'
            func_dict['did']=info['didvalue']
            func_dict['desc']='None'
            func_dict['sync']=sync
            func_dict['func_name']=func.text
            func_list.append(func_dict)
        res_text="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataReadFnc"
        func=info['diddata'].find('./%sPARAMETER-VALUES/%sECUC-TEXTUAL-PARAM-VALUE/[%sDEFINITION-REF="%s"]/%sVALUE'%(ns,ns,ns,res_text,ns))
        func_dict={}
        if func is not None:
            func_dict['type']='read'
            func_dict['did']=info['didvalue']
            func_dict['desc']='None'
            func_dict['sync']=sync
            func_dict['func_name']=func.text
            func_list.append(func_dict)
        res_text="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataWriteFnc"
        func=info['diddata'].find('./%sPARAMETER-VALUES/%sECUC-TEXTUAL-PARAM-VALUE/[%sDEFINITION-REF="%s"]/%sVALUE'%(ns,ns,ns,res_text,ns))
        func_dict={}
        if func is not None:
            func_dict['type']='write'
            func_dict['did']=info['didvalue']
            func_dict['desc']='None'
            func_dict['sync']=sync
            func_dict['func_name']=func.text
            func_list.append(func_dict)
        return func_list
    def get_ecu_short_name(self,ecu):
        name=ecu.find('%sSHORT-NAME'%(ns))
        if name is not None:
            return name.text
        else:
            return None
    def get_ecu_by_name(self,name):
        for ecu in self.ecu_list:
            if ecu.find('./[%sSHORT-NAME="%s"]'%(ns,name)) is not None:
                return ecu
        return None
    def get_dcm_func_list(self):
        ecu_info_all=self.get_ecu_info_all()
        func_list=[]
        for info in ecu_info_all:
            if self.is_not_dynamically_did(info['didinfo']):
                func_list+=self.get_ecu_func(info)
        return func_list
    def get_ecu_info_all(self):
        ecu_info_all=[]
        for ecu in self.ecu_list:
            ecu_info={}
            try:
                dref=ecu.find('./[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid"]'%(ns))
                if dref is not None:
                    didinfo=ecu.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidInfoRef"]/%sVALUE-REF'%(ns,ns,ns))
                    if didinfo is None:
                        continue
                    didinfo=didinfo.text.split('/')[-1]
                    didinfo=self.get_ecu_by_name(didinfo)
                    if not self.is_not_dynamically_did(didinfo):
                        continue
                    diddata=ecu.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidSignal/DcmDspDidDataRef"]/%sVALUE-REF'%(ns,ns,ns))
                    if diddata is None:
                        continue
                    diddata=diddata.text.split('/')[-1]
                    diddata=self.get_ecu_by_name(diddata)
                    didvalue=ecu.find('.//%sECUC-NUMERICAL-PARAM-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidIdentifier"]/%sVALUE'%(ns,ns,ns))
                    if didvalue is None:
                        continue
                    didvalue='0x%04X'%(int(didvalue.text))
                    ecu_info['didinfo']=didinfo
                    ecu_info['diddata']=diddata
                    ecu_info['didvalue']=didvalue
                    ecu_info_all.append(ecu_info)
            except ValueError:
                pass
        return ecu_info_all
    def append_dcm_ecu(self,ecu):
        if type(ecu) is str:
            ecu=ET.fromstring(ecu)
        ecu.tail='\n'+' '*18
        dcm_ecu=self.root.find('.//%sECUC-CONTAINER-VALUE/[%sSHORT-NAME="DcmDsp"]/%sSUB-CONTAINERS'%(ns,ns,ns))
        dcm_ecu[-1].tail='\n'+' '*20
        dcm_ecu.append(ecu)
        return self.tree
    def append_dcm_ecu_list(self,ecu_list):
        dcm_ecu=self.root.find('.//%sECUC-CONTAINER-VALUE/[%sSHORT-NAME="DcmDsp"]/%sSUB-CONTAINERS'%(ns,ns,ns))
        dcm_ecu[-1].tail='\n'+' '*20
        for ecu in ecu_list:
            if type(ecu) is str:
                ecu=ET.fromstring(ecu)
            ecu.tail='\n'+' '*20
            dcm_ecu.append(ecu)
        dcm_ecu[-1].tail='\n'+' '*18
        return self.tree
    def check_dcm_ecu_exists(self,did_hex):
        dcm_ecu=self.root.find('.//%sECUC-CONTAINER-VALUE/[%sSHORT-NAME="DcmDsp"]/%sSUB-CONTAINERS'%(ns,ns,ns))
        for ecu in list(dcm_ecu):
            didvalue=ecu.find('.//%sECUC-NUMERICAL-PARAM-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidIdentifier"]/%sVALUE'%(ns,ns,ns))
            if didvalue is not None and int(didvalue.text)==int(did_hex,16):
                return True
        return False
    def remove_dcm_ecu_by_did(self,did_hex):
        dcm_ecu=self.root.find('.//%sECUC-CONTAINER-VALUE/[%sSHORT-NAME="DcmDsp"]/%sSUB-CONTAINERS'%(ns,ns,ns))
        for ecu in list(dcm_ecu):
            didvalue=ecu.find('.//%sECUC-NUMERICAL-PARAM-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidIdentifier"]/%sVALUE'%(ns,ns,ns))
            if didvalue is not None and int(didvalue.text)==int(did_hex,16):
                ecu_did=ecu
                didinfo=ecu.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidInfoRef"]/%sVALUE-REF'%(ns,ns,ns))
                didinfo=didinfo.text.split('/')[-1]
                ecu_didinfo=self.get_ecu_by_name(didinfo)
                diddata=ecu.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidSignal/DcmDspDidDataRef"]/%sVALUE-REF'%(ns,ns,ns))
                diddata=diddata.text.split('/')[-1]
                ecu_diddata=self.get_ecu_by_name(diddata)
                datainfo=ecu_diddata.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataInfoRef"]/%sVALUE-REF'%(ns,ns,ns))
                datainfo=datainfo.text.split('/')[-1]
                ecu_datainfo=self.get_ecu_by_name(datainfo)
                for ecu in [ecu_did,ecu_didinfo,ecu_diddata,ecu_datainfo]:
                    if ecu in list(dcm_ecu):
                        dcm_ecu.remove(ecu)
                break
        return self.tree
        #self.tree.write(self.xml_path,encoding="utf-8",xml_declaration=True)
    def remove_all_data_did_info(self):
        del_list=[]
        dcm_ecu=self.root.find('.//%sECUC-CONTAINER-VALUE/[%sSHORT-NAME="DcmDsp"]/%sSUB-CONTAINERS'%(ns,ns,ns))
        data_list=dcm_ecu.findall('./%sECUC-CONTAINER-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData"]'%(ns,ns))
        for ecu in data_list:
            diddata=ecu.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataInfoRef"]/%sVALUE-REF'%(ns,ns,ns))
            diddata=diddata.text.split('/')[-1]
            ecu_datainfo=self.get_ecu_by_name(diddata)
            if ecu_datainfo not in del_list:
                del_list.append(ecu_datainfo)
        del_list+=data_list
        did_list=dcm_ecu.findall('./%sECUC-CONTAINER-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid"]'%(ns,ns))
        for ecu in did_list:
            didinfo=ecu.find('.//%sECUC-REFERENCE-VALUE/[%sDEFINITION-REF="/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidInfoRef"]/%sVALUE-REF'%(ns,ns,ns))
            didinfo=didinfo.text.split('/')[-1]
            ecu_didinfo=self.get_ecu_by_name(didinfo)
            if ecu_didinfo not in del_list:
                del_list.append(ecu_didinfo)
        del_list+=did_list
        for ecu in del_list:
            if ecu in list(dcm_ecu):
                dcm_ecu.remove(ecu)
        return self.tree

    def MakeObjectXml(self, did_obj=None, data_obj=None):
        if did_obj is None:
            return '', '', '', ''
        didinfo_xml = ''
        didinfo_xml += ' ' * 20 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
            self.GetEcuUUID(), self.ends)
        didinfo_xml += ' ' * 22 + '<SHORT-NAME>%s</SHORT-NAME>%s' % (
            did_obj['DidInfoName'], self.ends)
        didinfo_xml += ' ' * 22 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo</DEFINITION-REF>%s' % (
            self.ends)
        didinfo_xml += ' ' * 22 + '<PARAMETER-VALUES>%s' % (self.ends)
        didinfo_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (
            self.ends)
        didinfo_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-BOOLEAN-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidDynamicallyDefined</DEFINITION-REF>%s' % (
            self.ends)
        didinfo_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
            str(did_obj['Define']).lower(), self.ends)
        didinfo_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (
            self.ends)
        didinfo_xml += ' ' * 22 + '</PARAMETER-VALUES>%s' % (self.ends)
        didinfo_xml += ' ' * 22 + '<SUB-CONTAINERS>%s' % (self.ends)
        didinfo_xml += ' ' * 24 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
            self.GetEcuUUID(), self.ends)
        didinfo_xml += ' ' * 26 + '<SHORT-NAME>DcmDspDidAccess</SHORT-NAME>%s' % (
            self.ends)
        didinfo_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess</DEFINITION-REF>%s' % (
            self.ends)
        didinfo_xml += ' ' * 26 + '<SUB-CONTAINERS>%s' % (self.ends)
        if did_obj['Define']:
            didinfo_xml += ' ' * 28 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
                self.GetEcuUUID(), self.ends)
            didinfo_xml += ' ' * 30 + '<SHORT-NAME>DcmDspDidDefine</SHORT-NAME>%s' % (
                self.ends)
            didinfo_xml += ' ' * 30 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidDefine</DEFINITION-REF>%s' % (
                self.ends)
            didinfo_xml += ' ' * 30 + '<PARAMETER-VALUES>%s' % (self.ends)
            didinfo_xml += ' ' * 32 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
            didinfo_xml += ' ' * 34 + '<DEFINITION-REF DEST="ECUC-INTEGER-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidDefine/DcmDspDDDidMaxElements</DEFINITION-REF>%s' % (
                self.ends)
            didinfo_xml += ' ' * 34 + '<VALUE>%s</VALUE>%s' % (
                str(self.DDidMaxElements), self.ends)
            didinfo_xml += ' ' * 32 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
            didinfo_xml += ' ' * 30 + '</PARAMETER-VALUES>%s' % (self.ends)
            didinfo_xml += ' ' * 28 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        if did_obj['Control']:
            didinfo_xml += ' ' * 28 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
                self.GetEcuUUID(), self.ends)
            didinfo_xml += ' ' * 30 + '<SHORT-NAME>DcmDspDidControl</SHORT-NAME>%s' % (
                self.ends)
            didinfo_xml += ' ' * 30 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidControl</DEFINITION-REF>%s' % (
                self.ends)
            if False:
                didinfo_xml += ' ' * 30 + '<REFERENCE-VALUES>%s' % (self.ends)
                didinfo_xml += ' ' * 32 + '<ECUC-REFERENCE-PARAM-VALUE>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 34 + '<DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidWrite/DcmDspDidControlSessionRef</DEFINITION-REF>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 34 + '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/ActiveEcuC/Dcm/DcmConfigSet/DcmDsp/DcmDspSession/Extended</VALUE-REF>' % (
                    self.ends)
                didinfo_xml += ' ' * 32 + '</ECUC-REFERENCE-PARAM-VALUE>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 30 + '</REFERENCE-VALUES>%s' % (self.ends)
            didinfo_xml += ' ' * 28 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        if did_obj['Write']:
            didinfo_xml += ' ' * 28 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
                self.GetEcuUUID(), self.ends)
            didinfo_xml += ' ' * 30 + '<SHORT-NAME>DcmDspDidWrite</SHORT-NAME>%s' % (
                self.ends)
            didinfo_xml += ' ' * 30 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidWrite</DEFINITION-REF>%s' % (
                self.ends)
            if False:
                didinfo_xml += ' ' * 30 + '<REFERENCE-VALUES>%s' % (self.ends)
                didinfo_xml += ' ' * 32 + '<ECUC-REFERENCE-PARAM-VALUE>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 34 + '<DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidWrite/DcmDspDidWriteSessionRef</DEFINITION-REF>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 34 + '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/ActiveEcuC/Dcm/DcmConfigSet/DcmDsp/DcmDspSession/Extended</VALUE-REF>' % (
                    self.ends)
                didinfo_xml += ' ' * 32 + '</ECUC-REFERENCE-PARAM-VALUE>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 30 + '</REFERENCE-VALUES>%s' % (self.ends)
            didinfo_xml += ' ' * 28 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        if did_obj['Read']:
            didinfo_xml += ' ' * 28 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
                self.GetEcuUUID(), self.ends)
            didinfo_xml += ' ' * 30 + '<SHORT-NAME>DcmDspDidRead</SHORT-NAME>%s' % (
                self.ends)
            didinfo_xml += ' ' * 30 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidRead</DEFINITION-REF>%s' % (
                self.ends)
            if False:
                didinfo_xml += ' ' * 30 + '<REFERENCE-VALUES>%s' % (self.ends)
                didinfo_xml += ' ' * 32 + '<ECUC-REFERENCE-PARAM-VALUE>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 34 + '<DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDidInfo/DcmDspDidAccess/DcmDspDidWrite/DcmDspDidReadSessionRef</DEFINITION-REF>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 34 + '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/ActiveEcuC/Dcm/DcmConfigSet/DcmDsp/DcmDspSession/Extended</VALUE-REF>' % (
                    self.ends)
                didinfo_xml += ' ' * 32 + '</ECUC-REFERENCE-PARAM-VALUE>%s' % (
                    self.ends)
                didinfo_xml += ' ' * 30 + '</REFERENCE-VALUES>%s' % (self.ends)
            didinfo_xml += ' ' * 28 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        didinfo_xml += ' ' * 26 + '</SUB-CONTAINERS>%s' % (self.ends)
        didinfo_xml += ' ' * 24 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        didinfo_xml += ' ' * 22 + '</SUB-CONTAINERS>%s' % (self.ends)
        didinfo_xml += ' ' * 20 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        did_xml = ''
        did_xml += ' ' * 20 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
            self.GetEcuUUID(), self.ends)
        did_xml += ' ' * 22 + '<SHORT-NAME>%s</SHORT-NAME>%s' % (
            did_obj['DidName'], self.ends)
        did_xml += ' ' * 22 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid</DEFINITION-REF>%s' % (
            self.ends)
        did_xml += ' ' * 22 + '<PARAMETER-VALUES>%s' % (self.ends)
        did_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (self.ends)
        did_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-INTEGER-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidIdentifier</DEFINITION-REF>%s' % (
            self.ends)
        did_xml += ' ' * 26 + '<VALUE>%d</VALUE>%s' % (did_obj['Did'],
                                                       self.ends)
        did_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (self.ends)
        did_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (self.ends)
        did_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-BOOLEAN-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidUsed</DEFINITION-REF>%s' % (
            self.ends)
        did_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
            str(did_obj['Used']).lower(), self.ends)
        did_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (self.ends)
        if True:
            did_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
            did_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-ENUMERATION-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidUsePort</DEFINITION-REF>%s' % (
                self.ends)
            did_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
                'USE_DATA_ELEMENT_SPECIFIC_INTERFACES', self.ends)
            did_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
        did_xml += ' ' * 22 + '</PARAMETER-VALUES>%s' % (self.ends)
        did_xml += ' ' * 22 + '<REFERENCE-VALUES>%s' % (self.ends)
        did_xml += ' ' * 24 + '<ECUC-REFERENCE-VALUE>%s' % (self.ends)
        did_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidInfoRef</DEFINITION-REF>%s' % (
            self.ends)
        did_xml += ' ' * 26 + '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/ActiveEcuC/Dcm/DcmConfigSet/DcmDsp/%s</VALUE-REF>%s' % (
            did_obj['DidInfoName'], self.ends)
        did_xml += ' ' * 24 + '</ECUC-REFERENCE-VALUE>%s' % (self.ends)
        did_xml += ' ' * 22 + '</REFERENCE-VALUES>%s' % (self.ends)
        if data_obj is not None:
            did_xml += ' ' * 22 + '<SUB-CONTAINERS>%s' % (self.ends)
            did_xml += ' ' * 24 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
                self.GetEcuUUID(), self.ends)
            did_xml += ' ' * 26 + '<SHORT-NAME>DcmDspDidSignal</SHORT-NAME>%s' % (
                self.ends)
            did_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidSignal</DEFINITION-REF>%s' % (
                self.ends)
            did_xml += ' ' * 26 + '<PARAMETER-VALUES>%s' % (self.ends)
            did_xml += ' ' * 28 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
            did_xml += ' ' * 30 + '<DEFINITION-REF DEST="ECUC-INTEGER-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidSignal/DcmDspDidDataPos</DEFINITION-REF>%s' % (
                self.ends)
            did_xml += ' ' * 30 + '<VALUE>0</VALUE>%s' % (self.ends)
            did_xml += ' ' * 28 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
            did_xml += ' ' * 26 + '</PARAMETER-VALUES>%s' % (self.ends)
            did_xml += ' ' * 26 + '<REFERENCE-VALUES>%s' % (self.ends)
            did_xml += ' ' * 28 + '<ECUC-REFERENCE-VALUE>%s' % (self.ends)
            did_xml += ' ' * 30 + '<DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDid/DcmDspDidSignal/DcmDspDidDataRef</DEFINITION-REF>%s' % (
                self.ends)
            did_xml += ' ' * 30 + '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/ActiveEcuC/Dcm/DcmConfigSet/DcmDsp/%s</VALUE-REF>%s' % (
                data_obj['DataName'], self.ends)
            did_xml += ' ' * 28 + '</ECUC-REFERENCE-VALUE>%s' % (self.ends)
            did_xml += ' ' * 26 + '</REFERENCE-VALUES>%s' % (self.ends)
            did_xml += ' ' * 24 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
            did_xml += ' ' * 22 + '</SUB-CONTAINERS>%s' % (self.ends)
        did_xml += ' ' * 20 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        datainfo_xml = ''
        datainfo_xml += ' ' * 20 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
            self.GetEcuUUID(), self.ends)
        datainfo_xml += ' ' * 22 + '<SHORT-NAME>%s</SHORT-NAME>%s' % (
            data_obj['DataInfoName'], self.ends)
        datainfo_xml += ' ' * 22 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDataInfo</DEFINITION-REF>%s' % (
            self.ends)
        datainfo_xml += ' ' * 22 + '<PARAMETER-VALUES>%s' % (self.ends)
        datainfo_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (
            self.ends)
        datainfo_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-BOOLEAN-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspDataInfo/DcmDspDataFixedLength</DEFINITION-REF>%s' % (
            self.ends)
        datainfo_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
            str(data_obj['FixedLength']).lower(), self.ends)
        datainfo_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (
            self.ends)
        datainfo_xml += ' ' * 22 + '</PARAMETER-VALUES>%s' % (self.ends)
        datainfo_xml += ' ' * 20 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        if data_obj is None:
            return didinfo_xml, did_xml, '', ''
        data_xml = ''
        data_xml += ' ' * 20 + '<ECUC-CONTAINER-VALUE UUID="%s">%s' % (
            self.GetEcuUUID(), self.ends)
        data_xml += ' ' * 22 + '<SHORT-NAME>%s</SHORT-NAME>%s' % (
            data_obj['DataName'], self.ends)
        data_xml += ' ' * 22 + '<DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData</DEFINITION-REF>%s' % (
            self.ends)
        data_xml += ' ' * 22 + '<PARAMETER-VALUES>%s' % (self.ends)
        data_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (self.ends)
        data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-INTEGER-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataSize</DEFINITION-REF>%s' % (
            self.ends)
        data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
            str(data_obj['DataBitSize']), self.ends)
        data_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (self.ends)
        data_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
        data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-ENUMERATION-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataUsePort</DEFINITION-REF>%s' % (
            self.ends)
        data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
            data_obj['DataUsePort'], self.ends)
        data_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
        data_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
        data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-ENUMERATION-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataType</DEFINITION-REF>%s' % (
            self.ends)
        data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (data_obj['DataType'],
                                                        self.ends)
        data_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
        if len(data_obj['ConditionCheckReadFnc']) > 0:
            data_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
            data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-FUNCTION-NAME-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataConditionCheckReadFnc</DEFINITION-REF>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
                data_obj['ConditionCheckReadFnc'], self.ends)
            data_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (
                self.ends)
            data_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-BOOLEAN-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataConditionCheckReadFncUsed</DEFINITION-REF>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<VALUE>true</VALUE>%s' % (self.ends)
            data_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
        else:
            data_xml += ' ' * 24 + '<ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-BOOLEAN-PARAM-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataConditionCheckReadFncUsed</DEFINITION-REF>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<VALUE>false</VALUE>%s' % (self.ends)
            data_xml += ' ' * 24 + '</ECUC-NUMERICAL-PARAM-VALUE>%s' % (
                self.ends)
        if len(data_obj['DataReadLengthFnc']) > 0:
            data_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
            data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-FUNCTION-NAME-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataReadDataLengthFnc</DEFINITION-REF>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
                data_obj['DataReadLengthFnc'], self.ends)
            data_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (
                self.ends)
        if len(data_obj['DataWriteFnc']) > 0:
            data_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
            data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-FUNCTION-NAME-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataWriteFnc</DEFINITION-REF>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
                data_obj['DataWriteFnc'], self.ends)
            data_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (
                self.ends)
        if len(data_obj['DataReadFnc']) > 0:
            data_xml += ' ' * 24 + '<ECUC-TEXTUAL-PARAM-VALUE>%s' % (self.ends)
            data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-FUNCTION-NAME-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataReadFnc</DEFINITION-REF>%s' % (
                self.ends)
            data_xml += ' ' * 26 + '<VALUE>%s</VALUE>%s' % (
                data_obj['DataReadFnc'], self.ends)
            data_xml += ' ' * 24 + '</ECUC-TEXTUAL-PARAM-VALUE>%s' % (
                self.ends)
        data_xml += ' ' * 22 + '</PARAMETER-VALUES>%s' % (self.ends)
        data_xml += ' ' * 22 + '<REFERENCE-VALUES>%s' % (self.ends)
        data_xml += ' ' * 24 + '<ECUC-REFERENCE-VALUE>%s' % (self.ends)
        data_xml += ' ' * 26 + '<DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/MICROSAR/Dcm/DcmConfigSet/DcmDsp/DcmDspData/DcmDspDataInfoRef</DEFINITION-REF>%s' % (
            self.ends)
        data_xml += ' ' * 26 + '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/ActiveEcuC/Dcm/DcmConfigSet/DcmDsp/%s</VALUE-REF>%s' % (
            data_obj['DataInfoName'], self.ends)
        data_xml += ' ' * 24 + '</ECUC-REFERENCE-VALUE>%s' % (self.ends)
        data_xml += ' ' * 22 + '</REFERENCE-VALUES>%s' % (self.ends)
        data_xml += ' ' * 20 + '</ECUC-CONTAINER-VALUE>%s' % (self.ends)
        return didinfo_xml, did_xml, datainfo_xml, data_xml

        #return (ecu_did,ecu_didinfo,ecu_diddata,ecu_datainfo)
    def argxml_wrtie(self,xml_path):
        xml_str=ET.tostring(self.root,encoding='unicode')
        xml_str='<?xml version="1.0" encoding="utf-8" standalone="no"?>\n'+xml_str
        with open(xml_path,'w',encoding='utf-8') as f:
            f.write(xml_str)
if __name__=="__main__":
    import os
    xml_path="C:\Project\GAC39\ConfigurationView_SC2_1S\DaVinciConfigurator_FFI\Config\ECUC\SC2_1S_Dcm_ecuc.arxml"
    out_path=os.path.basename(xml_path)
    xml_parse=ArxmlParse(xml_path)
    #func_list=xml_parse.get_dcm_func_list()
    #tree=xml_parse.remove_dcm_ecu_by_did('0xFDAB')
    tree=xml_parse.remove_all_data_did_info()
    tree.write('copy_'+out_path,encoding="utf-8",xml_declaration=True)
