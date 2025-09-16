# SOMA Tools

from sys import exit

from deps.utils import *
from deps.reader import *
from deps.xml import XMLNode



GAME_DIR = r'G:\Steam\steamapps\common\SOMA'
SHADER_KINDS = [ 'vs', 'fs' ]



def splitShaders ():
    xmlPath  = joinPath(GAME_DIR, '_shadersource', 'shadercache.xml')
    hpssPath = joinPath(GAME_DIR, '_shadersource', 'shadersource.hpss')
    outDir   = joinPath(GAME_DIR, '_shadersource', 'split')

    createDirs(outDir)

    bulk  = readBin(hpssPath)
    xml   = XMLNode(readBin(xmlPath))
    nodes = xml.findAll('Cache/Shader')

    for i, node in enumerate(nodes):
        name  = node.getAttribute('Name')
        kind  = int(node.getAttribute('ShaderType'))
        start = int(node.getAttribute('SourceStart'))
        end   = int(node.getAttribute('SourceEnd'))

        print(name)

        name = f'{(i + 1):03d}_{name[:64]}.{SHADER_KINDS[kind]}.glsl'
        data = bulk[start:end]

        shaderPath = joinPath(outDir, name)

        writeBin(shaderPath, data)


def collectUserVars (rootNode):
    varsNode = rootNode.find('UserDefinedVariables')

    userVars = {}

    for varNode in varsNode.findAll('Var'):
        name  = varNode.getAttribute('Name')
        value = varNode.getAttribute('Value')

        userVars[name] = value

    return {
        'params': varsNode.getAttributes(),
        'vars': userVars
    }


def buildEntityScheme (rootDir):
    tree = {}

    def walk (node, acc):
        tagName = node.getTag()

        nodeAcc = acc[tagName] = acc.get(tagName, {})
        nodeAttrs = nodeAcc['@attrs'] = nodeAcc.get('@attrs', [])

        for key in node.getAttrKeys():
            if key not in nodeAttrs:
                nodeAttrs.append(key)
                nodeAttrs.sort()

        for childNode in node.getChildren():
            walk(childNode, nodeAcc)

        return acc

    for filePath in iterFiles(rootDir, True, [ '.ent' ]):
        rootNode = XMLNode(readBin(filePath), encoding='cp1252')
        walk(rootNode, tree)

    print(toJson(tree))


def parseModel (entPath):
    print(entPath)

    rootNode = XMLNode(readBin(entPath), encoding='cp1252')

    # userVars = collectUserVars(rootNode)

    # modelNode = rootNode.find('ModelData')

    # assert modelNode and modelNode.hasChildren(), entPath

    # entitiesNode = modelNode.find('Entities')

    # print(rootNode.getChildren())
    # exit()


def parseModels (rootDir):
    for filePath in iterFiles(rootDir, True, [ '.ent' ]):
        parseModel(filePath)


if __name__ == '__main__':
    # splitShaders()
    # parseModel(joinPath(GAME_DIR, 'entities', 'character', 'deepsea_diver', 'deepsea_diver_monster', 'deepsea_diver_monster.ent'))
    # parseModels(joinPath(GAME_DIR, 'entities'))
    buildEntityScheme(joinPath(GAME_DIR, 'entities'))