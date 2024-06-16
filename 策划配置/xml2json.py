#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import shutil
import json
import xmltodict
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding('utf-8')


__version__ = '0.1'



class XML2Json(object):
    '''transfer xml to json'''
    def __init__(self,xml_name, json_dir=None):
        if not os.path.exists(xml_name):
            print "Doesn't exist XML file: ", xml_name
            sys.exit(-1)
        self.xml = xml_name
        self.content = ''
        if json_dir and not os.path.exists(json_dir):
            os.mkdir(json_dir)
        new_file = os.path.basename(xml_name)[1:][:-4] + ".json"
        self.outfile = os.path.join(json_dir, new_file)
        self.json = {} 
        self.json_dir = json_dir
        # print self.outfile

    def handleXML(self):
        with open(self.xml) as f:
            self.dictData = xmltodict.parse(f.read())


    def doTransfer(self,dict_data):
        if isinstance(dict_data, list):
            self.content += "["
            for item in dict_data:
                self.doTransfer(item)
            self.content += "],"
        elif isinstance(dict_data, OrderedDict):
            if ("#text" in dict_data.keys()):
                self.doTransfer(dict_data["#text"])
            else:
                self.content += "{"
                for key in dict_data.keys():
                    keyTemp = key
                    if key[0] == '@':
                        keyTemp = key[1:]
                    self.content += "\"" + keyTemp + "\": "
                    self.doTransfer(dict_data[key])
                self.content += "},"
        else:
            if dict_data == None  or len(dict_data) == 0:
                self.content += ""
                return
            value =  ""
            dict_data = dict_data.replace("\"", "")
            try:
                value = int(dict_data)
            except ValueError:
                try:
                    value = float(dict_data)
                except ValueError:
                    value = "\"" + dict_data + "\""
            try:
                value = str(value)
            except UnicodeEncodeError:
                pass
            self.content += value + ","

    def handleId(self):
        data = self.content.replace(',}','}').replace(',]',']')[:-1]
        data = data.replace('\n','')
        jsonObj = None
        try:
            jsonObj = json.loads(data)
        except ValueError:
            print "Wrong xml: ", self.xml
        if jsonObj:
            data = jsonObj['clientRoot']['data']
            if isinstance(data, list):
                for item in data:
                    obj = {}
                    try:
                        self.json[item['id']] = item
                    except TypeError:
                        obj = item
                        print "Wrong Item in ",self.xml, item
                    #self.json.append(obj)
            elif isinstance(data,dict):
                self.json[data['id']] = data
    def writeToJson(self):
        with open(self.outfile,'w') as f:
            jsonObj = json.dumps(self.json, ensure_ascii=False)
            f.write(jsonObj)

    def xml2json(self):
        self.handleXML()
        self.doTransfer(self.dictData)
        self.handleId()
        self.writeToJson()


def main(xml_dir=None, json_dir=None):
    files = os.listdir( xml_dir == '.' and os.curdir or xml_dir )
    if os.path.exists(json_dir):
        shutil.rmtree(json_dir)
        os.mkdir(json_dir)
    for filename in files:
        fileExt = filename[-3:]
        # TODO: check if the xml file has been modified
        # if not ,then doesn't to process
        if fileExt == "xml":
            x2j = XML2Json(os.path.join(xml_dir,filename), json_dir)
            x2j.xml2json()


def help():
    print "usage: python xml2json xml_dir json_dir"



if __name__ == "__main__":
    if len(sys.argv) != 3:
        help()
        sys.exit(-1)

    main(sys.argv[1],sys.argv[2])
