import re

# pip install lxml
from lxml import etree

from .utils import readBin


XML_NAMESPACE_REGEX = re.compile(r'^\{([^\}]+)\}')


# https://lxml.de/tutorial.html
class XMLNode:
    def __init__ (self, source, encoding='utf-8'):
        if isinstance(source, etree._Element):
            self._node = source
        elif isinstance(source, bytes):
            parser = etree.XMLParser(encoding=encoding)
            self._node = etree.fromstring(source, parser=parser)
        else:
            raise Exception('No source. Expected bytes or etree._Element')

        self.isComment = isinstance(source, etree._Comment)

        self._namespaces = {
            '': self._extractNamespace(self._node)
        }

    def __str__ (self):
        return f'<{ self.__class__.__name__ } \'{ self.getTag() }\'>'

    def __repr__ (self):
        return self.__str__()

    def __len__ (self):
        return len(self._node)

    def __bool__ (self):
        return True

    def _extractNamespace (self, node):
        if self.isComment:
            return None

        match = re.findall(XML_NAMESPACE_REGEX, node.tag) 

        return match[0] if match else None

    def _dropTagNamespace (self, tag):
        return re.sub(XML_NAMESPACE_REGEX, '', tag) 

    def getTag (self):
        if self.isComment:
            return None

        return self._dropTagNamespace(self._node.tag)

    def find (self, pattern):
        node = self._node.find(pattern, namespaces=self._namespaces)

        return XMLNode(node) if node is not None else None

    def findAll (self, pattern):
        nodes = self._node.findall(pattern, namespaces=self._namespaces)

        return [ XMLNode(node) for node in nodes ]

    def getText (self):
        return self._node.text or ''

    def setText (self, text):
        self._node.text = text

    def getAttribute (self, name, default=None):
        return self._node.get(name, default)

    def getAttributes (self):
        return self._node.attrib

    def getAttrKeys (self):
        return self._node.keys()

    def getParent (self):
        return XMLNode(self._node.getparent())

    def remove (self):
        parentNode = self._node.getparent()

        if parentNode is not None:
            parentNode.remove(self._node)
            return True

        return False

    # Only tags are taken into account
    def hasChildren (self):
        return len(self._node) > 0

    # Only tags are taken into account
    def getChildren (self):
        children = self._node.getchildren()

        return [ XMLNode(child) for child in children ]

    # Tags and text nodes are taken into account
    def getContentItems (self):  
        nodes = []

        for node in self._node.xpath('child::node()'):
            if isinstance(node, (etree._ElementStringResult, etree._ElementUnicodeResult)):
                node = str(node).strip()
            else:
                node = XMLNode(node)

            if node:
                nodes.append(node)

        return nodes

    '''
    # TODO: remake in non-recursive way
    def toJson (self):
        def walker (node):
            entry = {
                'tag': None,
                'isComment': False,
                'attributes': [],
                'content': None
            }

            if isinstance(node, etree._Comment):
                entry['isComment'] = True
                entry['content']   = node.text or ''
            else:
                entry['tag'] = self._dropTagNamespace(node.tag)

        return walker(self._node)
    '''

    def serialize (self):
        etree.indent(self._node, space='    ')
        data = etree.tostring(self._node, encoding='utf-8', xml_declaration=True, pretty_print=True)

        return data


def __test__ ():
    data = readBin(r'D:\Documents\Downloads\rfc-index.xml')

    root = XMLNode(data)

    entries = root.findAll('rfc-entry')

    print(len(entries))  



__all__ = [
    'etree',
    'XMLNode'
]  



if __name__ == '__main__':
    __test__()
