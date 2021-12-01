from collections import namedtuple
import os
import re

WHITE_SPACES = " " * 4

class ReactComponent:
    #name, propName, props, state, callbacks, docstring
    def __init__(self, name, propName, file):
        self.name = name
        self.file = file
        self.propName = propName
        self.content = open(self.file, "r", encoding="utf8").read()
        self.index = self.content.index(self.name)
        self.docstring = "<<empty>>"
        self.props = {}
        self.state = []
        self.methods = []
        self.children = {}

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
        start_index = self.content[self.index:].find("{")       + self.index
        end_index = self.content[self.index:].find("return")    + self.index
        function_regex = r"const\s*(\w+)\s*=\s*\([^\)]*\)\s*=>"
        
        self.methods = re.findall(function_regex, self.content[start_index:end_index])
        

    def parseChildren(self):
        # global var of all components has to be defined

        for component in COMPONENT_NAMES:
            if component == self.name:
                continue
            if re.search(f"<{component}(\s|>)", self.content, re.IGNORECASE):
                self.children.append(component)
        
        #self.children = {component for component in COMPONENT_NAMES if f"<{component} " in self.content and component != self.name} # <comp(blenk) to see if correct comp


    def __str__(self):
        return f"{self.name}, {self.propName}, {self.file}"

    def to_plant_uml(self):
        
        
        desc = WHITE_SPACES + self.docstring
        # props
        props = "==props==\n" + "\n".join([WHITE_SPACES + "#" + prop for prop in self.props])
        state = "==state==\n" + "\n".join([WHITE_SPACES + "#" + state for state in self.state])
        methods = "==methods==\n" + "\n".join([WHITE_SPACES + "+" + method for method in self.methods])
        
        body = f"\n{WHITE_SPACES}".join((desc, props, state, methods))
        header_body = f"class \"{self.name}\" << (C,blue) component >> {{\n{body}\n}}"
        return header_body
    


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
COMPONENT_NAMES = [comp.name for comp in components if comp]
components = [comp for comp in components if comp]


all_uml = []
for comp in components:
    #comp.parseProps()
    #print(comp.name)
    #print(comp.props)
    comp.parseProps()
    comp.parseState()
    comp.parseMethods()
    comp.parseChildren()
    all_uml.append(comp.to_plant_uml())

CONNECTION_TYPE = "o--"

def generate_connections(components):
    
    connections = []
    for comp in components:
        print(comp.name + ": " + repr(comp.children))
        for child in comp.children:
            connections.append(f"{comp.name} {CONNECTION_TYPE} {child}")

    return connections
            


start = "\n".join(("@startuml", "title Title", "skinparam dpi 300"))
end = "\n@enduml"
all_classes = "\n\n".join(all_uml)
all_connections = "\n".join(generate_connections(components))
diagram_txt = "\n".join((start, all_classes, all_connections, end))



open("generated.txt", "w").write(diagram_txt)

