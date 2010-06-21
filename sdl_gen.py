from xml.etree import ElementTree as ET
from time import gmtime, strftime
from sys import argv

def print_node(node):   
	print "=============================================="  
	print "node.attrib:%s" % node.attrib   
	if node.attrib.has_key("age") > 0 :   
		print "node.attrib['age']:%s" % node.attrib['age']   
	print "node.tag:%s" % node.tag   
	print "node.text:%s" % node.text 


def walk_tree(root):   
	lst_node = root.getiterator("person")   
	for node in lst_node:   
		print_node(node)

def par_set_foreach(Elem, **par):
	for i in par.iteritems():
		Elem.set(i[0], i[1])

def build_defaultDocument(Parent, Store_in):
	par_dic = {
		"backup":"false", "launchable":"false", 
		"caching":"default", "encoding":"Big5", 
		"indexFeeds":"false", "urlInfo":"true"
	}

	defaultDocument = ET.SubElement(Parent, "defaultDocument")
	par_set_foreach(defaultDocument, **par_dic)

	source = ET.SubElement(defaultDocument, "source")
	source.set("maxLinkDepth", "1")

	images = ET.SubElement(defaultDocument, "images")
	par_dic = {
		"maxWidth":"320", "maxHeight":"320", 
		"bpp":"16", "alternate":"false", 
		"enabled":"true"
	}
	par_set_foreach(images, **par_dic)

	destinations = ET.SubElement(defaultDocument, "destinations")
	directory = ET.SubElement(destinations, "directory")
	directory.text = Store_in


def build_document(Parent, name, category, URI, Store_in):
	now = strftime("%Y-%m-%dT%H:%m:%M", gmtime())
	par_dic = {
		"backup":"false", "launchable":"false", 
		"caching":"default", "encoding":"Big5", 
		"indexFeeds":"false", "urlInfo":"true", 
		"size":"", "created":"", "lastConverted":"", 
		"lastUpdated":"", "lastAttempted":"", 
	}

	document = ET.SubElement(Parent, "document")
	par_set_foreach(document, **par_dic)

	_name = ET.SubElement(document, "name")
	_name.text = name

	_category = ET.SubElement(document, "category")
	_category.text = category

	par_dic = {
		"maxLinkDepth":"1", "checksum":""
	}
	source = ET.SubElement(document, "source")
	par_set_foreach(source, **par_dic)
	source.text = URI

	par_dic = {
		"maxWidth":"320", "maxHeight":"320", 
		"bpp":"16", "alternate":"false", 
		"enabled":"true", 
	}
	images = ET.SubElement(document, "images")
	par_set_foreach(images, **par_dic)

	destinations = ET.SubElement(document, "destinations")
	directory = ET.SubElement(destinations, "directory")
	directory.text = Store_in


rss_page_name = ("Supplement", "Finance", "International", 
	"Sport", "HeadLine", "Estate", "Home")
url = "http://localhost:8000/public_html/" + argv[1] + "/"

root = ET.Element("documentList")
root.set("xmlns", "http://www.distantchord.com/sdl/")

build_defaultDocument(root, "./")

for name in rss_page_name:
	build_document(root, name, "MY", url + name + "_RSS.html", "./")

#build_document(root, "Home", "MY", 
#	"http://localhost:8000/Home_RSS.html", "./")

tree = ET.ElementTree(root)
tree.write("app2rss.sdl")

