from collections import namedtuple
import os
import re

class ReactComponent:
    #name, propName, props, state, callbacks, docstring
    def __init__(self, name, propName, file):
        self.name = name
        self.file = file
        self.propName = propName
        self.content = open(self.file, "r", encoding="utf8").read()
        self.index = self.content.index(self.name)
        self.docstring = "<<empty>>"
        self.props = []
        self.state = []
        self.methods = []
        self.children = []

    def parseDocstring(self):
         # fetch first javadoc before comment
        doc_index = self.content[:self.index].rfind("/**")
        if doc_index == -1:
            return
        end_index = self.content[doc_index:self.index].find("*/") + doc_index # no cut of
        
        javadoc = self.content[doc_index:end_index].split("\n")
        # transform javadoc
        trailing_stars = [line.strip() for line in javadoc[1:] if line.strip() != "*"]
        plain_text = [line[1:].strip() for line in trailing_stars if line.startswith("*")]
        self.docstring = "\n".join(plain_text)

    def parseState(self):
        start_index = self.content[self.index:].find("{")       + self.index
        end_index = self.content[self.index:].find("return")    + self.index
        
        lines = self.content[start_index:end_index].split("\n")
        for line in lines:
            mo = re.search(r"const\s*\[\s*(\w+)\s*,\s*\w+\s*\]\s*=\s*React.useState\(.*", line)
            if mo:
                self.state.append(mo.group(1))

    def parseProps(self):
        if not self.propName:
            return
        regex = f"{self.propName}\\.(\w+)"
        self.props = set(re.findall(regex, self.content[self.index:]))

    def parseMethods(self):
        pass

    def parseChildren(self):
        pass


    def __str__(self):
        return f"{self.name}, {self.propName}, {self.file}"


BASE_DIR = "../pse-prototype/src"

File = namedtuple("File", ("name", "path"))

def get_component_info(lines):
    for line in lines:
        mo = re.search(".*function\s+(\w+)\s*\((\w*)\)\s*.*", line)
        if mo:
            if mo.group(1)[0].isupper(): # assumes that only react components start with Uppercase
                return (mo.group(1), mo.group(2))

def parse_file(fileObj):
    lines = open(fileObj.path, "r", encoding="utf-8").readlines()
    data = get_component_info(lines)
    if not data:
        return
    react_comp = ReactComponent(name=data[0], propName=data[1], file=fileObj.path)
    return react_comp
    
   
                




all_files = []
for path, subdirs, files in os.walk(BASE_DIR):
    for name in files:
        f = File(name, os.path.join(path, name))
        all_files.append(f)

files = [f for f in all_files if f.name.endswith(".js")]


components = [parse_file(f) for f in files]
componentNames = [comp.name for comp in components if comp]
components = [comp for comp in components if comp]

for comp in components:
    comp.parseProps()
    print(comp.name)
    print(comp.props)

