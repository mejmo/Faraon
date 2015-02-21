import operator
import random
import colorsys
import pylab
import getopt
import sys
import os
import coverage

from treemap import Treemap
from coverageutils import CoveredCode, CoveredModule


def example():    
    """
    Treemap demo!
    
    This shows an example of creating a treemap  of nested tuples, random colours.
    Node size is sum of leaf elements.
    """ 
    
    size_cache = {}
    
    def size(thing):
        """sum size of child nodes"""
        if isinstance(thing, int) or isinstance(thing, float):
            return thing
        if thing in size_cache:
            return size_cache[thing]
        else:
            size_cache[thing] = reduce(operator.add, [size(x) for x in thing])
            return size_cache[thing]
    
    def random_color(thing):
        """just return a random color"""
        return colorsys.hsv_to_rgb(random.random(), 0.5, 1)
    
    tree = ((5, (3, 5, 2, (0.1, 0.1, 0.6), 1)), 4, 
            (5, 2, (2, 3, (3, 2, (2, 5, 2), 2)), 
             (3, 3)), (3, 2, (0.2, 0.2, 0.2)))
    

    tm = Treemap(tree, size, random_color)    
    pylab.show()
    
    
def test_coverage():
    """Treemap visualisation of coverage information.
    
    This script will visually display a coverage file generated by Ned
    Batchelders statment coverage module, coverage.py (available from 
    http://www.nedbatchelder.com/code/modules/coverage.html).  Each node
    in the treemap is a python module with size is given by the number 
    of lines of code and colour of the by the coverage. Red is no coverage, 
    green is full coverage.  Mouse hovering will show the name of the file.
    
    The script automatically looks in the current directory for a 
    .coverage file to display.  Else you can specify a file using the first
    argument.  e.g.
    
        treemap_coverage /path/to/.coverage
    
    You can include or exclude modules using --include or --exclude.  For 
    example, to exclude all files in the treemap package:
    
        treemap_coverage --exclude treemap /path/to/.coverage
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:ve:v", ["help", "include=", "exclude="])
    except getopt.GetoptError:
        print test_coverage.__doc__
        sys.exit(2)
        
    coverage_file = ".coverage"
    include = None
    exclude = "Test"
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print test_coverage.__doc__
            sys.exit()
        if o in ("-i", "--include"):
            include = a
        if o in ("-e", "--exclude"):
            exclude = a    
            
    if len(args) > 0:
        coverage_file = args[0]
    
    if not os.path.exists(coverage_file):
        print "%s: file does not exist (try --help)" % coverage_file
        sys.exit(2)

    coverage.the_coverage.cache = coverage_file
    try:
        coverage.the_coverage.restore()
    except:
        print "Error loading coverage, is %s a valid coverage file?" % coverage_file
    
    wanted = coverage.the_coverage.cexecuted.keys()
    
    if include:    
        wanted = [x for x in wanted if x.count(include)]
    if exclude:
        wanted = [x for x in wanted if not x.count(exclude)]
    wanted = [coverage.the_coverage.canonical_filename(x) for x in wanted]
    
    
    code = CoveredCode(wanted)
    root = code.root_module()
    
    Treemap( root,  code.size, code.color, iter_method=code.child_modules )
    pylab.show()
    
