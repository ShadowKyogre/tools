#!/usr/bin/python
"""
This file is part of AardDict (http://code.google.com/p/aarddict) - 
a dictionary for Nokia Internet Tablets. 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2008  Jeremy Mortis and Igor Tkach
"""
import logging

import sys
import cStringIO
from htmlentitydefs import name2codepoint
import re

class SimpleXMLParser:

    def __init__(self):
        pass

    def parseString(self, string):
        file = cStringIO.StringIO(string)
        self.parseFile(file)
        
    def parseFile(self, file):
        buffer = ""
        buflen = 0
        bufpos = 1
        tag = ""
        data = ""
        
        while True:

            if bufpos >= buflen:
                buffer = file.read(100000)
                buflen = len(buffer)
                bufpos = 0
                
            if not buffer:
                break
            
            if tag:
                pos = buffer.find(">", bufpos)
                if pos >= 0:
                    tag += buffer[bufpos:pos+1]
                    bufpos = pos+1
                    if tag.startswith("<!--"):
                        if tag.endswith("-->"):
                            tag = ""
                            continue
                        else:
                            continue
                    else:
                        self.processTag(tag)
                        inTag = False
                        tag = ""
                        continue
                else:
                    tag += buffer[bufpos:]
                    bufpos = buflen
                    continue

            pos = buffer.find("<", bufpos)
            if pos == -1:
                data += buffer[bufpos:]
                # don't split "&nbsp;" etc.
                if buffer[-5:].find("&") == -1:
                    self.processData(data)
                    data = ""
                bufpos = buflen
            else:
                if pos > bufpos:
                    data += buffer[bufpos:pos]
                self.processData(data)
                data = ""
                bufpos = pos + 1
                tag = "<"

        self.handleCleanup()
        
    def processTag(self, tag):
        tag = tag[1:-1]
        tag = tag.replace("\n", " ")

        if not tag:
            return
        if tag[0] == '/':
            tag = tag.replace(" ", "")
            self.handleEndElement(tag[1:])
        elif tag[-1] == '/':
            tag = tag[:-1]
            tagElements = tag.split(" ")
            self.handleStartElement(tagElements[0], self.makeAttrDict(tagElements[1:]))
            self.handleEndElement(tagElements[0])
        else:
            tagElements = tag.split(" ")
            self.handleStartElement(tagElements[0], self.makeAttrDict(tagElements[1:]))
            

    def makeAttrDict(self, tokens):
        attrDict = {}

        # handle quoted strings containing spaces
        i = 0
        while i < len(tokens):
            if tokens[i] == "":
                tokens.pop(i)
            elif (tokens[i].count('"') == 1) and (i+1 < len(tokens)):
                tokens[i] = tokens[i] + " " + tokens[i+1]
                tokens.pop(i+1)
            elif (tokens[i].count("'") == 1) and (i+1 < len(tokens)):
                tokens[i] = tokens[i] + " " + tokens[i+1]
                tokens.pop(i+1)
            else:
                i = i + 1

        for t in tokens:
            sep = t.find("=")
            if sep == -1:
                name = t
                value = ""
            else:
                name = t[:sep]
                value = t[sep+1:]
            if value and (value[0] == '"') and (value[-1] == '"'):
                value = value[1:-1]
            if value and (value[0] == "'") and (value[-1] == "'"):
                value = value[1:-1]
            attrDict[unescape(name)] = unescape(value)
        return attrDict

    def processData(self, data):
        self.handleCharacterData(unescape(data))

    def handleStartElement(self, tag, attrsList):
        # usually overridden
        sys.stderr.write("XML start tag: <%s> %s\n" % (tag, str(attrsList)))

    def handleEndElement(self, tag):
        # usually overridden
        sys.stderr.write("XML end tag: </%s>\n" % tag)
        
    def handleCharacterData(self, data):
        # usually overridden
        sys.stderr.write("XML data: '%s'\n" % data)

    def handleCleanup(self):
        # usually overridden
        sys.stderr.write("XML cleanup\n")

def handle_entityref(m):
    name = m.group(1)
    if name in name2codepoint:
        return unichr(name2codepoint[name])
    elif name.startswith(u'#'):
        return unichr(int(name[1:]))
    else:
        return "&"+name

entity_pattern = re.compile('&(#*\w+);')

def unescape(s):
    try:    
        return re.sub(entity_pattern, handle_entityref, s.decode('utf8')).encode('utf8')
    except:
        logging.exception('unescape failed')
        return s

        
if __name__ == '__main__':
    import sys

    p = SimpleXMLParser() 
    s = '''
    <h1
    >This is a &quot;title&quot;</h1><br>\n<a href="there"
    class=x>this<br/><i class='yyy'>and</i>  <!---ignore me <really> -->zz
    asdfffffffffffsssssssssssssssssssssssssssssssssssssssssssssssss
    ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
    fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg
    hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh
    iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
    lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll
    <b>that</i><span selected></b></a><minor /><a href="big &quot;daddy&quot; o">yow&nbsp;za</a>
    '''
    print s
    
    p.parseString(s)

    print "Done."





