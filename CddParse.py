# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:44:02 2018

@author: levy.he
"""

import xml.etree.ElementTree as ET
import uuid

class Cdd(object):
    def __init__(self,cdd_path):
        self.cdd_path = cdd_path
        self.tree = ET.parse(cdd_path)
        self.root = self.tree.getroot()
        self._id_list = self.GET_ID_LIST()
        self.GET_ECU_RefId()

    def cdd_wrtie(self,cdd_path):
        xml_str=ET.tostring(self.root,encoding='unicode').replace('"',"'")
        xml_str="<?xml version='1.0' encoding='utf-8' standalone='no'?>\n<!DOCTYPE CANDELA SYSTEM 'candela.dtd'>\n"+xml_str
        with open(cdd_path,'w',encoding='utf-8') as f:
            f.write(xml_str)
    def Generate_oid(self):
        oid = str(uuid.uuid4())
        return oid.replace('-', '')
    def Generate_temploid(self):
        return str(uuid.uuid4()).replace('-', '')
    def Generate_id(self, start_id=0x01000000):
        while int(start_id) in self._id_list:
            start_id += 1
        self._id_list.append(start_id)
        return '_%08X'%(start_id)
    def GET_ID_LIST(self):
        id_list = [x.attrib['id'].replace('_','0x') for x in self.root.findall('.//*[@id]')]
        id_list = [int(x, 16) for x in id_list]
        id_list.sort()
        return id_list

    def GET_DCLTMPLS(self):
        return self.root.find('./ECUDOC/DCLTMPLS')
    def GET_ECU_RefId(self):
        dctml = self.GET_DCLTMPLS().find('./DCLTMPL/[QUAL="ECU_Identification"]')
        if dctml is None:
            raise Exception('invalid cdd file')
        self._ecu_tmpref_id = dctml.attrib['id']
        read_tmp = dctml.find('./DCLSRVTMPL/[QUAL="Read"]')
        self._ecu_readref_id = read_tmp.attrib['id']
        write_tmp = dctml.find('./DCLSRVTMPL/[QUAL="Write"]')
        self._ecu_writeref_id = write_tmp.attrib['id']
        record_tmp = dctml.find('./SHSTATIC/[QUAL="RecordDataIdentifier"]')
        self._ecu_recordref_id = record_tmp.attrib['id']
        datarecord_tmp = dctml.find('./SHPROXY/[QUAL="DataRecord"]')
        self._ecu_recordref_data = datarecord_tmp.attrib['id']
        read_tmp = dctml.find('./SHPROXY/[QUAL="Read"]')
        self._ecu_readref_data = read_tmp.attrib['id']
        write_tmp = dctml.find('./SHPROXY/[QUAL="Write"]')
        self._ecu_writeref_data = write_tmp.attrib['id']
    def GET_NRC_MessageId(self,v):
        nrcs = self.root.find('./ECUDOC/NEGRESCODES/NEGRESCODE[@v="%d"]'%(v))
        if nrcs is not None:
            return nrcs.attrib['id']

    def GET_PROTOCOLSERVICES(self):
        return self.root.find('./ECUDOC/PROTOCOLSERVICES')
    def GTE_DATATYPES(self):
        return self.root.find('./ECUDOC/DATATYPES')
    def Get_ECU_Sessions(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Sessions"]')
    def Get_ECU_FaultMemory(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGINST/[QUAL="FaultMemory"]')
    def Get_ECU_Stored_Data(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Stored_Data"]')
    def Get_ECU_ECU_Identification(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="ECU_Identification"]')
    def Get_ECU_Variant_Coding(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Variant_Coding"]')
    def Get_ECU_Dynamic_Data(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Dynamic_Data"]')
    def Get_ECU_Periodic_Data(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Periodic_Data"]')
    def Get_ECU_Dynamically_Define_Periodic_Data(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Dynamically_Define_Periodic_Data"]')
    def Get_ECU_Dynamically_Define_Non_Periodic_Data(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Dynamically_Define_Non_Periodic_Data"]')
    def Get_ECU_IOControl(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="IOControl"]')
    def Get_ECU_Routine_Control(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Routine_Control"]')
    def Get_ECU_SecurityAccess(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="SecurityAccess"]')
    def Get_ECU_Communication_Control(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGCLASS/[QUAL="Communication_Control"]')
    def Get_ECU_ControlDTCSetting(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGINST/[QUAL="ControlDTCSetting"]')
    def Get_ECU_TesterPresent(self):
        return self.root.find('./ECUDOC/ECU/VAR/DIAGINST/[QUAL="TesterPresent"]')
    def Get_ECU_DID_ALL(self):
        return self.Get_ECU_ECU_Identification().findall("DIAGINST[@tmplref='%s']" % (self._ecu_tmpref_id))
    def Get_All_DataTypeRef(self):
        return self.root.findall('.//*[@dtref]')
    def Get_DataTyeID_ByQual(self,qual):
        dtref=self.GTE_DATATYPES().find('./*/[QUAL="%s"]'%(qual))
        if dtref is not None:
            return dtref.attrib['id']
    def Get_UsedDataTypes(self):
        dtref_list = [x.attrib['dtref'] for x in list(self.Get_All_DataTypeRef())]
        return [x for x in list(self.GTE_DATATYPES()) if x.attrib['id'] in dtref_list]
    def Get_UnusedDataTypes(self):
        dtref_list = [x.attrib['dtref'] for x in list(self.Get_All_DataTypeRef())]
        return [x for x in list(self.GTE_DATATYPES()) if x.attrib['id'] not in dtref_list]
    def Remove_UnsuedDataTypes(self):
        datatypes=self.GTE_DATATYPES()
        dtref_list = [x.attrib['dtref'] for x in list(self.Get_All_DataTypeRef())]
        dtref_list=list(set(dtref_list))
        for x in list(datatypes):
            if x.attrib['id'] not in dtref_list:
                datatypes.remove(x)
        return self.tree
    def Remove_ALLECUIdentification(self):
        ecus=self.Get_ECU_ECU_Identification()
        for x in ecus.findall('DIAGINST'):
            ecus.remove(x)
        return self.tree
    def Remove_AllPeriodicData(self):
        ecus=self.Get_ECU_Periodic_Data()
        for x in ecus.findall('DIAGINST'):
            ecus.remove(x)
        return self.tree
    def Remove_AllDynamicData(self):
        ecus=self.Get_ECU_Dynamic_Data()
        for x in ecus.findall('DIAGINST'):
            ecus.remove(x)
        return self.tree
    def Remove_DynamicallyDefinePeriodicData(self):
        ecus=self.Get_ECU_Dynamically_Define_Periodic_Data()
        for x in ecus.findall('DIAGINST'):
            ecus.remove(x)
        return self.tree
    def IsDatatypeshasSameQualName(self,qual):
        if self.root.find('./ECUDOC/DATATYPES/*/[QUAL="%s"]'%(qual)) is not None:
            return True
        else:
            return False
    def DatatypeAppend(self,xml):
        if type(xml) is str:
            xml=ET.fromstring(xml)
        xml.tail='\n'
        datatype=self.GTE_DATATYPES()
        datatype[-1].tail='\n'
        datatype.append(xml)
        return self.tree

    def EcuDidAppend(self, xml):
        if type(xml) is str:
            xml = ET.fromstring(xml)
        xml.tail = '\n'
        datatype = self.Get_ECU_ECU_Identification()
        datatype[-1].tail = '\n'
        datatype.append(xml)
        return self.tree
    def UpdateEcuAttrs(self, obj):
        attrs = self.root.find('./ECUDOC/DEFATTS/ECUATTS/*/[QUAL="%s"]' %
                               (obj['Interface'] + '.' + obj['Item']))
        if attrs is not None:
            if attrs.tag == 'ENUMDEF':
                if obj['Value'] == '11_Bit':
                    attrs.attrib['v'] = '0'
                elif obj['Value'] == '29_Bit':
                    attrs.attrib['v'] = '1'
            elif attrs.tag == 'UNSDEF':
                attrs.attrib['v'] = str(int(obj['Value'], 16))
        else:
            print('error Can id param (%s)'%(obj['Item']))
        return self.tree
    def RawDataXMLMake(self,obj):
        '''
        Name: 
        Qual:
        TypeTag:
        DataType:
        MinSize:
        MaxSize:
        BSize:
        Unit:
        '''
        xml_str = ''
        if obj['DataType'] == 'ASCII':
            xml_str += "<IDENT bm='255' id='%s' oid='%s' temploid='%s'>\n" % (
                self.Generate_id(0x0D8F0000), self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n"
            xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n"%(obj['Name'])
            xml_str += "</NAME>\n"
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['Qual'])
            xml_str += "<CVALUETYPE bl='8' bo='21' df='text' enc='asc' maxsz='%d' minsz='%d' qty='field' sig='0' sz='no' />\n" % (
                obj['MaxSize'],obj['MinSize'])
            xml_str += "<PVALUETYPE bl='8' bo='21' df='text' enc='asc' maxsz='%d' minsz='%d' qty='field' sig='0' sz='no' />\n" % (
                obj['MaxSize'], obj['MinSize'])
            xml_str += "</IDENT>\n"
        elif obj['DataType'] == 'HEX':
            bm = (1 << int(obj['BSize'])) - 1
            if obj['MinSize'] == 1 and obj['MaxSize'] == 1:
                qty = 'atom'
            else:
                qty = 'field'
            xml_str += "<IDENT bm='%d' id='%s' oid='%s' temploid='%s'>\n" % (bm,
                self.Generate_id(0x0D8F0000), self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n"
            xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n" % (obj['Name'])
            xml_str += "</NAME>\n"
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['Qual'])
            xml_str += "<CVALUETYPE bl='%d' bo='21' df='hex' enc='uns' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' />\n" % (
                obj['BSize'],obj['MaxSize'], obj['MinSize'],qty)
            xml_str += "<PVALUETYPE bl='%d' bo='21' df='hex' enc='uns' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' />\n" % (
                obj['BSize'],obj['MaxSize'], obj['MinSize'],qty)
            xml_str += "</IDENT>\n"
        elif obj['DataType'] == 'DEC':
            bm = (1 << int(obj['BSize'])) - 1
            if obj['MinSize'] == 1 and obj['MaxSize'] == 1:
                qty = 'atom'
            else:
                qty = 'field'
            xml_str += "<IDENT bm='%d' id='%s' oid='%s' temploid='%s'>\n" % (
                bm, self.Generate_id(0x0D8F0000), self.Generate_oid(),
                self.Generate_temploid())
            xml_str += "<NAME>\n"
            xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n" % (obj['Name'])
            xml_str += "</NAME>\n"
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['Qual'])
            if len(obj['Unit']) > 0:
                xml_str += "<CVALUETYPE bl='%d' bo='21' df='dec' enc='uns' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' >\n" % (
                    obj['BSize'],obj['MaxSize'], obj['MinSize'], qty)
                xml_str += "<UNIT>%s</UNIT>\n</CVALUETYPE>\n"%(obj['Unit'])
                xml_str += "<PVALUETYPE bl='%d' bo='21' df='dec' enc='uns' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' >\n" % (
                    obj['BSize'],obj['MaxSize'], obj['MinSize'], qty)
                xml_str += "<UNIT>%s</UNIT>\n</PVALUETYPE>\n"%(obj['Unit'])
            else:
                xml_str += "<CVALUETYPE bl='%d' bo='21' df='dec' enc='uns' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' />\n" % (
                    obj['BSize'], obj['MaxSize'], obj['MinSize'],qty)
                xml_str += "<PVALUETYPE bl='%d' bo='21' df='dec' enc='uns' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' />\n" % (
                    obj['BSize'],obj['MaxSize'], obj['MinSize'],qty)
            xml_str += "</IDENT>\n"
        elif obj['DataType'] == 'BCD':
            bm = (1 << int(obj['BSize'])) - 1
            if obj['MinSize'] == 1 and obj['MaxSize'] == 1:
                qty = 'atom'
            else:
                qty = 'field'
            xml_str += "<IDENT bm='%d' id='%s' oid='%s' temploid='%s'>\n" % (
                bm, self.Generate_id(0x0D8F0000), self.Generate_oid(),
                self.Generate_temploid())
            xml_str += "<NAME>\n"
            xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n" % (obj['Name'])
            xml_str += "</NAME>\n"
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['Qual'])
            if len(obj['Unit']) > 0:
                xml_str += "<CVALUETYPE bl='%d' bo='21' df='dec' enc='bcd' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' >\n" % (
                    obj['BSize'],obj['MaxSize'], obj['MinSize'], qty)
                xml_str += "<UNIT>%s</UNIT>\n</CVALUETYPE>\n"%(obj['Unit'])
                xml_str += "<PVALUETYPE bl='%d' bo='21' df='dec' enc='bcd' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' >\n" % (
                    obj['BSize'],obj['MaxSize'], obj['MinSize'], qty)
                xml_str += "<UNIT>%s</UNIT>\n</PVALUETYPE>\n"%(obj['Unit'])
            else:
                xml_str += "<CVALUETYPE bl='%d' bo='21' df='dec' enc='bcd' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' />\n" % (
                    obj['BSize'], obj['MaxSize'], obj['MinSize'],qty)
                xml_str += "<PVALUETYPE bl='%d' bo='21' df='dec' enc='bcd' maxsz='%d' minsz='%d' qty='%s' sig='0' sz='no' />\n" % (
                    obj['BSize'],obj['MaxSize'], obj['MinSize'],qty)
            xml_str += "</IDENT>\n"
        return xml_str
    def LinearDataXMLMake(self, obj):
        '''
        Name: 
        Qual:
        TypeTag:
        DataType:
        BSize:
        Factor:
        Divisor:
        Offset:
        MinValue:
        MaxValue:
        DecimalPlaces:
        Unit:
        InvalidData:
        '''
        xml_str = ''
        bm = (1 << int(obj['BSize'])) - 1
        if obj['DataType'] == 'UNSIGNED':
            uns='uns'
        else:
            uns='sgn'
        xml_str += "<LINCOMP id='%s' oid='%s' temploid='%s' bm='%d'>\n"%(
            self.Generate_id(0x0D8F0000), self.Generate_oid(), self.Generate_temploid(), bm)
        xml_str += "<NAME>\n"
        xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n" % (obj['Name'])
        xml_str += "</NAME>\n"
        xml_str += "<QUAL>%s</QUAL>\n" % (obj['Qual'])
        xml_str += "<CVALUETYPE bl='%d' bo='21' enc='%s' sig='0' df='hex' qty='atom' sz='no' minsz='0' maxsz='255'/>\n"%(
            obj['BSize'], uns)
        for x in obj['InvalidData']:
            xml_str += "<EXCL s='%d' e='%d' inv='undef'>\n<TEXT>\n<TUV xml:lang='en-US'>Undefined</TUV>\n</TEXT>\n</EXCL>\n"%(
                x['start'], x['end'])
        if len(obj['Unit']) > 0:
            xml_str += "<PVALUETYPE bl='64' bo='21' enc='dbl' sig='%d' df='flt' qty='atom' sz='no' minsz='0' maxsz='255'>\n"%(
                obj['DecimalPlaces'])
            xml_str+="<UNIT>%s</UNIT>\n</PVALUETYPE>\n"%(obj['Unit'])
        else:
            xml_str += "<PVALUETYPE bl='64' bo='21' enc='dbl' sig='%d' df='flt' qty='atom' sz='no' minsz='0' maxsz='255' />\n"%(
                obj['DecimalPlaces'])
        xml_str += "<COMP "
        if obj['MinValue'] is not None and obj['MaxValue'] is not None:
            xml_str+="s='{0:n}' e='{1:n}' ".format(obj['MinValue'],obj['MaxValue'])
        xml_str+="f='{0:n}' div='{1:n}' o='{2:n}' >\n</COMP>\n".format(obj['Factor'],obj['Divisor'],obj['Offset'])
        xml_str += "</LINCOMP>\n"
        return xml_str
    def EnumDataXMLMake(self, obj):
        '''
        Name: 
        Qual:
        TypeTag:
        BSize:
        InvalidData:
        TextList:
            MinValue:
            MaxValue:
            AssignedText:
            AddInfo:
        '''
        xml_str = ''
        bm = (1 << int(obj['BSize'])) - 1
        xml_str += "<TEXTTBL id='%s' oid='%s' temploid='%s' bm='%d'>\n"%(
            self.Generate_id(0x0D8F0000), self.Generate_oid(), self.Generate_temploid(), bm)
        xml_str += "<NAME>\n"
        xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n" % (obj['Name'])
        xml_str += "</NAME>\n"
        xml_str += "<QUAL>%s</QUAL>\n" % (obj['Qual'])
        xml_str += "<CVALUETYPE bl='%d' bo='21' enc='uns' sig='0' df='hex' qty='atom' sz='no' minsz='1' maxsz='1'/>\n"%(obj['BSize'])
        for x in obj['InvalidData']:
            xml_str += "<EXCL s='%d' e='%d' inv='undef'>\n<TEXT>\n<TUV xml:lang='en-US'>Undefined</TUV>\n</TEXT>\n</EXCL>\n"%(
                x['start'], x['end'])
        xml_str += "<PVALUETYPE bl='16' bo='21' enc='utf' sig='0' df='text' qty='field' sz='no' minsz='0' maxsz='65535'/>\n"
        for text in obj['TextList']:
            xml_str += "<TEXTMAP s='%d' e='%d'>\n"%(text['MinValue'],text['MaxValue'])
            xml_str += "<TEXT>\n<TUV xml:lang='en-US'>%s</TUV>\n</TEXT>\n"%(text['AssignedText'])
            if len(text['AddInfo']) > 0:
                xml_str += "<ADDINFO>\n<TUV xml:lang='en-US'>%s</TUV>\n</ADDINFO>\n"%(text['AddInfo'])
            xml_str += "</TEXTMAP>\n"
        xml_str += "</TEXTTBL>\n"
        return xml_str
    def Make_Datatype_XML(self, obj):
        '''
        obj is a dict object with type define as follow:
        TypeTag: XML tag name 
        '''
        xml_str=''
        if obj['TypeTag'] == 'Raw':
            xml_str = self.RawDataXMLMake(obj)
        elif obj['TypeTag'] == 'Linear':
            xml_str = self.LinearDataXMLMake(obj)
        elif obj['TypeTag'] == 'Enum':
            xml_str = self.EnumDataXMLMake(obj)
        else:
            return None
        return ET.fromstring(xml_str)
    def Make_SubDataObject(self, obj):
        '''
        this function is used to make a data object which is a subeklement of 
        Ecu_Identification xml
        obj is a dict has keys define as follow:
        type: Resered,DataObj or BitField
        Name: name description
        Qual: a string like a variable name
        if type is Reserved obj has key bl
        '''
        xml_str=''
        if obj['ParamType'] == 'Reserved':
            xml_str += "<GAPDATAOBJ bl='%d' oid = '%s' temploid = '%s' >\n" % (
                obj['BitSize'], self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>%s</TUV>\n</NAME>\n"%(obj['ParamName'])
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['ParamQual'])
            xml_str += "</GAPDATAOBJ>\n"
        elif obj['ParamType'] == 'DataObj':
            xml_str += "<DATAOBJ dtref='%s' oid='%s' spec='no' temploid='%s'>\n" % (
                self.Get_DataTyeID_ByQual(obj['DtQualref']),
                self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>%s</TUV>\n</NAME>\n"%(obj['ParamName'])
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['ParamQual'])
            xml_str += "</DATAOBJ>\n"
        elif obj['ParamType'] == 'BitField':
            xml_str += "<STRUCT dtref='%s' oid='%s' spec='no' temploid='%s'>\n" % (
                self.Get_DataTyeID_ByQual(obj['DtQualref']),
                self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>%s</TUV>\n</NAME>\n"%(obj['ParamName'])
            xml_str += "<QUAL>%s</QUAL>\n" % (obj['ParamQual'])
            for x in obj['objlist']:
                xml_str +=self.Make_SubDataObject(x)
            xml_str += "</STRUCT>\n"
        return xml_str

    def Make_Ecu_Identification(self, obj):
        xml_str = ''
        xml_str += "<DIAGINST id='%s' oid='%s' req='notReq' temploid='%s' tmplref='%s'>\n" % (
            self.Generate_id(0x13EA0000), self.Generate_oid(),
            self.Generate_temploid(), self._ecu_tmpref_id)
        xml_str += "<NAME>\n"
        xml_str += "<TUV xml:lang='en-US'>%s</TUV>\n"%(obj['Name'])
        xml_str += "</NAME>\n"
        xml_str += "<QUAL>%s</QUAL>\n"%(obj['Qual'])
        if len(obj['Desc']) > 0:
            xml_str += "<DESC>\n"
            xml_str += "<TUV xml:lang='en-US' struct='1'>\n"
            for desc in obj['Desc'].splitlines():
                xml_str += "<PARA><FC fs='180'>%s</FC><PARA>\n"%(desc)
            xml_str += "</TUV>\n</DESC>\n"
        if obj['Read'] is not None:
            xml_str += "<SERVICE id='%s' oid='%s' temploid='%s' tmplref='%s' func='1' phys='1' respOnPhys='1' respOnFunc='1' req='0'>\n" % (
                self.Generate_id(0x13EA0000), self.Generate_oid(),
                self.Generate_temploid(), self._ecu_readref_id)
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>Read</TUV>\n</NAME>\n"
            xml_str += "<QUAL>Read</QUAL>\n"
            xml_str += "<SHORTCUTNAME>\n<TUV xml:lang='en-US'>%s</TUV>\n</SHORTCUTNAME>\n"%(obj['ReadName'])
            xml_str += "<SHORTCUTQUAL>%s</SHORTCUTQUAL>\n"%(obj['ReadQual'])
            xml_str += "</SERVICE>"
        if obj['Write'] is not None:
            xml_str += "<SERVICE id='%s' oid='%s' temploid='%s' tmplref='%s' func='1' phys='1' respOnPhys='1' respOnFunc='1' req='0'>\n" % (
                self.Generate_id(0x13EA0000), self.Generate_oid(),
                self.Generate_temploid(), self._ecu_writeref_id)
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>Write</TUV>\n</NAME>\n"
            xml_str += "<QUAL>Write</QUAL>\n"
            xml_str += "<SHORTCUTNAME>\n<TUV xml:lang='en-US'>%s</TUV>\n</SHORTCUTNAME>\n" % (obj['WriteName'])
            xml_str += "<SHORTCUTQUAL>%s</SHORTCUTQUAL>\n" % (obj['WriteQual'])
            xml_str += "</SERVICE>\n"
        xml_str += "<STATICVALUE oid='%s' temploid='%s' shstaticref='%s' v='%d'/>\n" % (
            self.Generate_oid(), self.Generate_temploid(),
            self._ecu_recordref_id, obj['Did'])
        xml_str += "<SIMPLECOMPCONT oid='%s' temploid='%s' shproxyref='%s'>\n" % (
            self.Generate_oid(), self.Generate_temploid(),self._ecu_recordref_data)
        for x in obj['Datalist']:
            xml_str += self.Make_SubDataObject(x)
        xml_str += "</SIMPLECOMPCONT>\n"
        if obj['Read'] is not None:
            xml_str += "<SIMPLECOMPCONT oid='%s' temploid='%s' shproxyref='%s'>\n" % (
                self.Generate_oid(), self.Generate_temploid(),
                self._ecu_readref_data)
            xml_str += "<SPECDATAOBJ oid='%s' temploid='%s'>\n" % (
                self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>Read</TUV>\n</NAME>\n"
            xml_str += "<QUAL>Read</QUAL>\n"
            xml_str += "<NEGRESCODEPROXIES>\n"
            for v in [19, 20, 34, 49]:
                v_id = self.GET_NRC_MessageId(v)
                if v_id is not None:
                    xml_str += "<NEGRESCODEPROXY idref='%s'/>\n"%(v_id)

            xml_str += "</NEGRESCODEPROXIES>\n</SPECDATAOBJ>\n</SIMPLECOMPCONT>\n"
        if obj['Write'] is not None:
            xml_str += "<SIMPLECOMPCONT oid='%s' temploid='%s' shproxyref='%s'>\n" % (
                self.Generate_oid(), self.Generate_temploid(),
                self._ecu_writeref_data)
            xml_str += "<SPECDATAOBJ oid='%s' temploid='%s'>\n" % (
                self.Generate_oid(), self.Generate_temploid())
            xml_str += "<NAME>\n<TUV xml:lang='en-US'>Write</TUV>\n</NAME>\n"
            xml_str += "<QUAL>Write</QUAL>\n"
            xml_str += "<NEGRESCODEPROXIES>\n"
            for v in [19, 34, 49, 51, 114, 126]:
                v_id = self.GET_NRC_MessageId(v)
                if v_id is not None:
                    xml_str += "<NEGRESCODEPROXY idref='%s'/>\n" % (v_id)
            xml_str += "</NEGRESCODEPROXIES>\n</SPECDATAOBJ>\n</SIMPLECOMPCONT>\n"
        xml_str += "</DIAGINST>\n"
        return ET.fromstring(xml_str)

    def Parse_DataType(self, xml_obj, start_bit=0):
        end_bit = start_bit
        if xml_obj.tag == 'IDENT':
            Name = xml_obj.find('QUAL').text
            cval = xml_obj.find('CVALUETYPE')
            pval = xml_obj.find('PVALUETYPE')
            bl = int(cval.attrib['bl'])
            maxsize = int(cval.attrib['maxsz']) * bl
            minsize = int(cval.attrib['minsz']) * bl
            Segments = int(cval.attrib['maxsz'])
            end_bit = start_bit + maxsize
            Signed = False
            PhyType = 'HEX'
            if cval.attrib['enc'] == 'asc':
                PhyType = 'ASCII'
            elif cval.attrib['enc'] == 'uns':
                if pval.attrib['df'] == 'dec':
                    PhyType = 'DEC'
                else:
                    PhyType = 'HEX'
            elif cval.attrib['enc'] == 'sgn':
                PhyType = 'DEC'
                Signed = True
            elif cval.attrib['enc'] == 'bcd':
                PhyType = 'BCD'
            unit = pval.get('UNIT')
            Unit = unit.text if unit else ''
            ByteOrder = 'big' if cval.attrib['bo'] == '21' else 'little'
            SubObj=None

        elif xml_obj.tag == 'LINCOMP':
            Name = xml_obj.find('QUAL').text
            cval = xml_obj.find('CVALUETYPE')
            pval = xml_obj.find('PVALUETYPE')
            comp = xml_obj.find('COMP')
            bl = int(cval.attrib['bl'])
            maxsize = bl
            minsize = bl
            Segments = 1
            end_bit = start_bit + maxsize
            Signed = False
            PhyType = 'LINEAR'
            ByteOrder = 'big' if cval.attrib['bo'] == '21' else 'little'
            if cval.attrib['enc'] == 'sgn':
                Signed = True
            unit = pval.get('UNIT')
            Unit = unit.text if unit else ''
            Factor = float(comp.attrib.get('f',1))
            Divisor = float(comp.attrib.get('div',1))
            Offset = float(comp.attrib.get('o',0))
            DecimalPlaces = int(pval.attrib['sig'])
            LinearObj = dict(Factor=Factor, Divisor=Divisor, Offset=Offset, DecimalPlaces=DecimalPlaces)
            SubObj = LinearObj
        elif xml_obj.tag == 'TEXTTBL':
            Name = xml_obj.find('QUAL').text
            cval = xml_obj.find('CVALUETYPE')
            pval = xml_obj.find('PVALUETYPE')
            textmaps = xml_obj.findall('TEXTMAP')
            bl = int(cval.attrib['bl'])
            maxsize = bl
            minsize = bl
            Segments = 1
            end_bit = start_bit + maxsize
            Signed = False
            PhyType = 'ENUM'
            Unit=''
            ByteOrder = 'big' if cval.attrib['bo'] == '21' else 'little'
            Texts = {}
            for x in textmaps:
                Texts[int(x.attrib['e'])] = x.find('TEXT/TUV').text
            SubObj = Texts
        else:
            #xml_obj.tag == 'STRUCTDT' or xml_obj.tag == 'MUXDT'
            Name = xml_obj.find('QUAL').text
            cval = xml_obj.find('CVALUETYPE')
            bl = int(cval.attrib['bl'])
            maxsize = int(cval.attrib['maxsz']) * bl
            minsize = int(cval.attrib['minsz']) * bl
            Segments = int(cval.attrib['maxsz'])
            end_bit = start_bit + maxsize
            Signed = False
            PhyType = 'HEX'
            Unit = ''
            ByteOrder = 'big'
            SubObj = None
        obj = dict(TypeName=Name, StartBit=start_bit, MinBitSize=minsize, MaxBitSize=maxsize, PhyType=PhyType, ObjType='Raw',
                   Unit=Unit, SubObj=SubObj, ByteOrder=ByteOrder, Signed=Signed, Segments=Segments)
        return obj, end_bit

    def Parse_SubDataObject(self, xml_obj, start_bit=0):
        end_bit = start_bit
        obj = {}
        if xml_obj.tag == 'GAPDATAOBJ':
            obj['TypeName'] = xml_obj.find('QUAL').text
            obj['Name'] = obj['TypeName']
            obj['StartBit'] = start_bit
            bitsize = int(xml_obj.attrib['bl'])
            end_bit = start_bit + bitsize
            obj['MinBitSize'] = bitsize
            obj['MaxBitSize'] = bitsize
            obj['PhyType'] = 'HEX'
            obj['Unit'] = ''
            obj['ByteOrder'] = 'big'
            obj['Signed'] = False
            obj['ObjType'] = 'Raw'
            obj['Segments'] = 1
            obj['SubObj'] = []
        elif xml_obj.tag == 'DATAOBJ':
            ref_id = xml_obj.attrib['dtref']
            Name = xml_obj.find('QUAL').text
            xml_data = self.GTE_DATATYPES().find("*[@id='%s']"%(ref_id))
            obj, end_bit = self.Parse_DataType(xml_data, start_bit)
            obj['Name'] = Name

        elif xml_obj.tag == 'STRUCT':
            ref_id = xml_obj.attrib['dtref']
            Name = xml_obj.find('QUAL').text
            xml_data = self.GTE_DATATYPES().find("*[@id='%s']"%(ref_id))
            obj, end_bit = self.Parse_DataType(xml_data, start_bit)
            obj['Name'] = Name
            obj['ObjType'] = 'BitField'
            PackList=[]
            b_start, b_end = 0, 0
            for x in xml_obj.findall('DATAOBJ'):
                t_obj, b_end = self.Parse_SubDataObject(x, b_start)
                b_start = b_end
                PackList.append(t_obj)
            obj['PackList'] = PackList
        else:
            obj['ObjType'] = 'NotDefined'
        return obj, end_bit

    def Parse_Ecu_Identification(self, xml_did):
        DidName = xml_did.find('QUAL').text
        Did = int(xml_did.find('STATICVALUE').attrib['v'])
        xml_data = xml_did.find("SIMPLECOMPCONT[@shproxyref='%s']" % (self._ecu_recordref_data))
        DataList=[]
        start_bit = 0
        for x in xml_data:
            obj, start_bit = self.Parse_SubDataObject(x, start_bit)
            DataList.append(obj)
        BitSize = start_bit
        return dict(Did=Did, DidName=DidName, DataList=DataList, BitSize=BitSize)

    def Parse_AllDids(self):
        Dids={}
        for x in self.Get_ECU_DID_ALL():
            x = self.Parse_Ecu_Identification(x)
            Dids[x['Did']] = x
        return Dids


if __name__=='__main__':
    # cdd_path = "458 MY23 CDD V23.36.0.rev0.01.cdd"
    cdd_path = 'GAC_A39_Internal.cdd'
    cdd=Cdd(cdd_path)
    for x in cdd.Get_ECU_DID_ALL():
        print(cdd.Parse_Ecu_Identification(x))

    # for x in cdd.GTE_DATATYPES():
    #     obj, end_bit = cdd.Parse_DataType(x)
    #     if obj['PhyType'] == 'Linear':
    #         print('end_bit:', end_bit)
    #         print(obj)

    #used_list = cdd.Get_UsedDataTypes()
    # tree=cdd.Remove_ALLECUIdentification()
    # unused_list=cdd.Get_UnusedDataTypes()
    # cdd.Remove_AllPeriodicData()
    # cdd.Remove_AllDynamicData()
    # cdd.Remove_DynamicallyDefinePeriodicData()
    #cdd.Remove_UnsuedDataTypes()
    # cdd.cdd_wrtie('cdd_test_used_t.cdd')
    #id_list=['_%08X'%(x) for x in cdd.GET_ID_LIST()]
    #id_std=cdd.Generate_id(0x132A9AE8)
    #id_std=cdd.Generate_id(0x032A9AE8)
    #print (id_std)
    #list_nr = list(set(id_list))
