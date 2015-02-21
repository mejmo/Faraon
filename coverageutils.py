import marshal
import sys
import coverage
import StringIO
import colorsys
import math
import getopt
import os

SEP = "."

class CoveredCode:
    def __init__(self, module_list):
        self.modules = {}
        self.coverage_cache = {}
        
        buffer = StringIO.StringIO("")
        print "building coverage report, this can be slow... (try setting --include or --exclude)"
        coverage.report(module_list, file=buffer)
        buffer.seek(0)
        print "done"
        
        
        for line in buffer.readlines():
            #print line.rstrip()
            tokens = line.split()
            if len(tokens) > 3 and tokens[0] != 'Name':
                try:
                    cm = CoveredModule(tokens[0], int(tokens[1]), int(tokens[2]))
                    self.modules[cm.name] = cm
                    if cm.name.endswith('__init__'):
                        name = cm.name[:-9]
                        self.modules[name] = CoveredModule(name, 0, None)
                        
                except:
                    pass
                    #print "Error parsing", line
        
        self.root_module().size = 0
        
    def parent_module(self, module):
        parent = ".".join(module.name.split(".")[:-1])
        if parent in self.modules:
            return self.modules[parent]
        else: 
            return None

    def child_modules(self, module):
        module_list = self.modules.values()
        if module.name == 'TOTAL':
            return self.primary_modules()
        else:
            return sorted( [x for x in module_list 
                            if x.name != module.name and x.name.startswith(module.name)
                            and x.depth() == 1+module.depth()] )
        
    def primary_modules(self):
        module_list = self.modules.values()
        primary_length = min([len(x.name.split(SEP)) for x in module_list
                              if x.name != 'TOTAL'])
        return sorted( [x for x in module_list
                        if x.name != 'TOTAL' and self.parent_module(x) is None ] )

    def root_module(self):
        if len(self.primary_modules()) == 1:
            return self.primary_modules()[0]
        else:
            return self.modules['TOTAL']
    
    def size(self, module):
        size = module.size
        for child in self.child_modules(module):
            size += self.size(child)
        return size
    
    def color(self, module):
        (h,s,v) = (self.cover_as_percent(module)*0.3, 0.8, 1)
        return colorsys.hsv_to_rgb(h,s,v)
    
    def cover_as_percent(self, module):
        #print "m", module,  module.coverage, "/", module.size

        if module.coverage is not None:
            if module.size == 0:
                return 1.0
            self.coverage_cache[module] = float(module.coverage) / module.size
        else:
            sizes = [x.size for x in self.child_modules(module)]
            coverages = [self.cover_as_percent(x) for x in self.child_modules(module)]
            if sum(sizes) == 0:
                return 0.0
            self.coverage_cache[module] =  sum([x*y for (x,y) in zip(sizes, coverages)]) / sum(sizes)
        return self.coverage_cache[module]

class CoveredModule:
    
    def __init__(self, name, size, coverage):
        if name.count("/"):
            name = name.replace("/", ".")
        name = name.lstrip(".")
        self.name = name
        self.size = size
        self.coverage = coverage
    
    def depth(self):
        return len(self.name.split(SEP))
    
    def __str__(self):
        return self.name 
    
    def __repr__(self):
        return self.name 

    def __hash__(self):
        return hash(self.name)
    
    def __cmp__(a,b):
        return cmp(a.name, b.name)