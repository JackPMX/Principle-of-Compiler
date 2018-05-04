# -*- coding: utf-8 -*-  

import string
import xml.dom.minidom as Dom 

_key = ("auto","break","case","char","const","continue","default", "do","double","else","enum","extern","float","for","goto","if","int","long","register","return","short","signed","static","sizeof","struct","switch","typedef","union","unsigned","void","volatile","while") 

_seprator = "(){}[];,"

_oprator = ("+","-","*","\\","%",">",">=","<","<=","=","==","!=","||","&&","!")
_abnormalChar = '@#$%^&*~' #标识符中可能出现的非法字符    

_syn = ''       #单词的种别码  
_p = 0          #下标  
_value = ''     #存放词法分析出的单词  
_content = ''   #程序内容  
_mstate = 0     #字符串的状态  
_cstate = 0     #字符的状态  
_dstate = 0     #整数和浮点数的状态  
_line = 1   
_token =[]
number = 0

#XML生成类
class XMLGenerator:  
    def __init__(self, xml_name):  
        self.doc = Dom.Document()  
        self.xml_name = xml_name  
          
    def createNode(self, node_name):  
        return self.doc.createElement(node_name)  
      
    def addNode(self, node, prev_node = None):  
        cur_node = node  
        if prev_node is not None:  
            prev_node.appendChild(cur_node)  
        else:  
            self.doc.appendChild(cur_node)  
        return cur_node  
  
    def setNodeAttr(self, node, att_name, value):  
        cur_node = node  
        cur_node.setAttribute(att_name, value)  
  
    def setNodeValue(self, cur_node, value):  
        node_data = self.doc.createTextNode(value)  
        cur_node.appendChild(node_data)  
  
    def genXml(self):  
        f = open(self.xml_name, "w")  
        f.write(self.doc.toprettyxml(indent = "\t", newl = "\n", encoding = "utf-8"))  
        f.close()  

#从c文件中得到源码 保存在长字符串_global
def getSrcFromFile():  
    global _content  
    myPro = open(r'test.c','r')  
  
    for line in myPro:  
        if line != '\n':  
            _content = "%s%s" %(_content,line.lstrip())
        else:  
            _content = "%s%s" %(_content,line)  
    myPro.close() 
    

#移除源码中的注释
#0状态：初始状态 1状态：/ 2状态：/* 3状态 /*……* 4状态 /*……*/（接受态）
#未考虑//类型的注释
def removeComment():
    global _content  
    state = 0  
    index = -1
    for c in _content: 
        index = index + 1  
          
        if state == 0:  
            if c == '/':  
                state = 1  
                startIndex = index  
              
        elif state == 1:  
            if c == '*':  
                state = 2
            elif c == '/':
                state = 4  
            else:  
                state = 0  
                  
        elif state == 2:  
            if c == '*':  
                state = 3  
            else:  
                pass  
          
        elif state == 3:  
            if c == '/':  
                endIndex = index + 1  
                comment = _content[startIndex:endIndex]  
                _content = _content.replace(comment,'')   
                index = startIndex - 1  
                state = 0  
                  
            elif c == '*':  
                pass  
            else:  
                state = 2  

#词法分析过程，判断出其类型为数字、保留字、标识符、分隔符、操作符几类，并排查标识符命名错误、字符或2字符串没有封闭等几类错误
#尚未实现对八进制十六进制非法数的判定
def analysis(mystr):   
    global _p,_value,_syn,_mstate,_dstate,_line,_cstate  
      
    _value = ''  
    ch = mystr[_p]  
    _p += 1  
    while ch == ' ':  
        ch = mystr[_p]  
        _p += 1  
    if ch in string.letters or ch == '_':    
        while ch in string.letters or ch in string.digits or ch == '_' or ch in _abnormalChar:  
            _value += ch  
            ch = mystr[_p]  
            _p += 1  
        _p -= 1  
          
        for abnormal in _abnormalChar:  
            if abnormal in _value:  
                _syn = '@-6'  
                break  
            else:  
                _syn = 'ID'  
          
        for s in _key:  
            if cmp(s,_value) == 0:  
                _syn = 'Keyword'              
                break  
              
    elif ch == '\"':                          
        while ch in string.letters or ch in '\"% ' :  
            _value += ch  
            if _mstate == 0:  
                if ch == '\"':  
                    _mstate = 1  
            elif _mstate == 1:  
                if ch == '\"':  
                    _mstate = 2  
  
            ch = mystr[_p]  
            _p += 1  
              
        if _mstate == 1:  
            _syn = '@-2'       
            _mstate = 0  
              
        elif _mstate == 2:  
            _mstate = 0  
            _syn = 'String'  
              
        _p -= 1      

#analyze digitals          
    elif ch in string.digits:  
        while ch in string.digits or ch == '.' or ch in string.letters:  
            _value += ch  
            if _dstate == 0:  
                if ch == '0':  
                    _dstate = 1  
                else:  
                    _dstate = 2  
                      
            elif _dstate == 1:  
                if ch == '.':  
                    _dstate = 3  
                elif ch == 'x' or ch =='X':
                    _dstate = 6
                else:  
                    _dstate = 5  
                      
            elif _dstate == 2:  
                if ch == '.':  
                    _dstate = 3  
                  
            ch = mystr[_p]  
            _p += 1  
          
        for char in string.letters :  
            if char in _value and _dstate!=6:  
                _syn = '@-7'   
                _dstate = 0  
                  
                  
        if _syn != '@-7':  
            if _dstate == 5:  
                _syn = 'Oct'   
                _dstate = 0  
            elif _dstate == 6:
                _syn = 'hex'
                _dstate = 0
            else:      
                _dstate = 0  
                if '.' not in _value:  
                    _syn = 'Dec'                 
                else:  
                    if _value.count('.') == 1:  
                        _syn = 'Fraction'                
                    else:  
                        _syn = '@-5'                   
        _p -= 1  
              
#analyze charactors                  
    elif ch == '\'':                      
        while ch in string.letters or ch in '@#$%&*\\\'\"':  
            _value += ch  
            if _cstate == 0:  
                if ch == '\'':  
                    _cstate = 1  
                      
            elif _cstate == 1:  
                if ch == '\\':  
                    _cstate = 2  
                elif ch in string.letters or ch in '@#$%&*':  
                    _cstate = 3  
                      
            elif _cstate == 2:  
                if ch in 'nt':  
                    _cstate = 3  
                      
            elif _cstate == 3:  
                if ch == '\'':  
                    _cstate = 4  
            ch = mystr[_p]  
            _p += 1  
          
        _p -= 1  
        if _cstate == 4:  
            _syn = 'Charactor'  
            _cstate = 0  
        else:  
            _syn = '@-4'   
            _cstate = 0  
#analyze oprators                      
    elif ch == '<':   
        _value = ch  
        ch = mystr[_p]  
          
        if ch == '=':             
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else:                     
            _syn = 'Oprator'  
          
    elif ch == '>':   
        _value = ch  
        ch = mystr[_p]  
          
        if ch == '=':            
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else:                    
            _syn = 'Oprator'  
              
    elif ch == '!':   
        _value = ch  
        ch = mystr[_p]  
          
        if ch == '=':             
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else:                     
            _syn = 'Oprator'  
              
          
    elif ch == '+':   
        _value = ch  
        ch = mystr[_p]  
          
        if ch =='+':             
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else :                    
            _syn = 'Oprator'  
          
    elif ch == '-':   
        _value = ch  
        ch = mystr[_p]  
          
        if ch =='-':              
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else :                    
            _syn = 'Oprator'  
              
    elif ch == '=':    
        _value = ch  
        ch = mystr[_p]  
          
        if ch =='=':             
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else :                    
            _syn = 'Oprator'  
      
    elif ch == '&':  
        _value = ch   
        ch = mystr[_p]  
          
        if ch == '&':             
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else:                     
            _syn = 'Oprator'  
              
    elif ch == '|':  
        _value = ch  
        ch = mystr[_p]  
          
        if ch == '|':                 
            _value += ch  
            _p += 1  
            _syn = 'Oprator'  
        else:                    
            _syn = 'Oprator'  
              
    elif ch == '*':              
        _value = ch  
        _syn = 'Oprator'  
          
    elif ch == '/':               
        _value = ch  
        _syn = 'Oprator'  
    elif ch == '%':
        _value = ch
        _syn = 'Oprator'

#analyze seprators
    elif ch in _seprator:
        _value = ch
        _syn = "Seprator"
    elif ch == '\n':  
        _syn = '@-1'  
 

if __name__ == '__main__':   
    getSrcFromFile()  

    removeComment() 
    print(_content)

    while _p != len(_content):  
        analysis(_content)  
        dictt = {'number':0,'value':'exvalue','type':'extype','line':1,'valid':'ture'}
        dictt['number']=number
        dictt['value']=_value
        dictt['line']=_line
        if _syn == '@-1':  
            _line += 1 
        elif _syn == '@-2':  
            print( 'String ' + _value + ' Not Completed! Error in line ' + str(_line) ) 
            dictt['type']='String'
            dictt['valid']='false'
            number = number + 1
            _token.append(dictt)
        elif _syn == '@-4':  
            print( 'Charater ' + _value + ' Not Completed! Error in line ' + str(_line)  )
            dictt['type']='Charactor'
            dictt['valid']='false'
            number = number + 1
            _token.append(dictt)
        elif _syn == '@-5':  
            print ('Digital ' + _value + ' Illegal! Error in line ' + str(_line) ) 
            dictt['type']='Digital'
            dictt['valid']='false'
            number = number + 1
            _token.append(dictt)
        elif _syn == '@-6':  
            print( 'Keyword' + _value + ' Containing illegal Charactor!Error in line ' + str(_line) ) 
            dictt['type']='Keyword'
            dictt['valid']='false'
            number = number + 1
            _token.append(dictt)
        elif _syn == '@-7':  
            print ('Digital ' + _value + ' Illegal! Containing Charactor! Error in line ' + str(_line)) 
            dictt['type']='Digital'
            dictt['valid']='false' 
            number = number + 1
            _token.append(dictt)
        else: 
            dictt['type']=_syn
            dictt['valid']='true'  
            number = number + 1
            _token.append(dictt) 
        

  
    myXmlGenerator = XMLGenerator("token.xml");
    node_project = myXmlGenerator.createNode("project")
    myXmlGenerator.setNodeAttr(node_project,"name","test.c")
    node_tokens = myXmlGenerator.createNode("tokens")
    myXmlGenerator.addNode(node = node_project)
    myXmlGenerator.addNode(node_tokens,node_project)

    for index in _token:
        if(len(index)==0):
            continue
        node_token = myXmlGenerator.createNode("token")
        node_number = myXmlGenerator.createNode("number")
        node_value = myXmlGenerator.createNode("value")
        node_type = myXmlGenerator.createNode("type")
        node_line = myXmlGenerator.createNode("line")
        node_valid = myXmlGenerator.createNode("valid")
        myXmlGenerator.setNodeValue(node_number,str(index['number']))
        myXmlGenerator.addNode(node_number,node_token)
        myXmlGenerator.setNodeValue(node_value,index['value'])
        myXmlGenerator.addNode(node_value,node_token)
        myXmlGenerator.setNodeValue(node_type,index['type'])
        myXmlGenerator.addNode(node_type,node_token)
        myXmlGenerator.setNodeValue(node_line,str(index['line']))
        myXmlGenerator.addNode(node_line,node_token)
        myXmlGenerator.setNodeValue(node_valid,index['valid'])
        myXmlGenerator.addNode(node_valid,node_token)
        myXmlGenerator.addNode(node_token,node_tokens)
    
    myXmlGenerator.genXml()




'''
        elif state == 4:
            tmp_count = 0 
            tmp_count = startIndex
            print _content[startIndex]
            com = ''
            while _content[tmp_count]!= '\n':
                com = com + _content[tmp_count]
                tmp_count = tmp_count + 1
            _content = _content.replace(com,'',1)
            index = startIndex-1
            state = 0
'''    