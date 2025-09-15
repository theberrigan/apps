import os, stat, sys, regex, shutil, hashlib, json
from enum import Enum
from lxml import etree
from collections import namedtuple

from tools.utils import *
from tools.vpc import VPCParser, Serializer


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SE_ROOT_DIR = os.path.join(ROOT_DIR, 'SE')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
SOLUTION_PATH = os.path.join(SE_ROOT_DIR, 'everything.sln')

INITIAL_FILES_JSON_PATH = os.path.join(DATA_DIR, 'initial_files.json')
INITIAL_VS_SOLUTIONS_JSON_PATH = os.path.join(DATA_DIR, 'initial_vs_solutions.json')

GAME_DIR = r'G:\Steam\steamapps\common\Half-Life 2'
GAME_BIN_DIR = os.path.join(GAME_DIR, 'bin')

PROJECT_FILE_EXTS = [
    '.vcxproj',
    '.vcxproj.filters',
    '.vcxproj.user',
    '.vcxproj.vpc_crc',
]

XML_NAMESPACE_REGEX = regex.compile(r'^\{([^\}]+)\}')
ALLOWED_BUILD_TYPES = [ 'Debug', 'Release' ]
ALLOWED_PLATFORMS = [ 'Win32' ]
CONFIGURATION_REGEX = regex.compile(r'^(Debug|Release)\|Win32$')
PROJECT_REGEX = regex.compile(r'^Project\("\{([^\}]+)\}"\)\s*=\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"\{([^\}]+)\}"$')
PROJECT_DEP_REGEX = regex.compile(r'^\{([^\}]+)\}\s*=\s*\{([^\}]+)\}$')

Project = namedtuple('Project', ('typeId', 'name', 'path', 'id', 'deps'))
ProjectDep = namedtuple('ProjectDep', ('projectId', 'depId'))


def splitPath (path):
    return [ comp for comp in regex.split(r'[\\\/]+', path) if comp ]


def comparablePath (path):
    return os.path.join(*splitPath(path)).lower()


EXCLUDED_PROJECTS = [
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.6.3/cryptest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.6.3/cryptdll.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.6.3/cryptlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.6.3/dlltest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.61/cryptdll.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.61/cryptest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.61/cryptlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/external/crypto++-5.61/dlltest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/freetype/builds/windows/vc2010/freetype.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/libpng/projects/vstudio/libpng/libpng.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/libpng/projects/vstudio/pngstest/pngstest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/libpng/projects/vstudio/pngtest/pngtest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/libpng/projects/vstudio/pngunknown/pngunknown.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/libpng/projects/vstudio/pngvalid/pngvalid.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/libpng/projects/vstudio/zlib/zlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/SDL/SDL.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/SDLmain/SDLmain.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/SDLtest/SDLtest.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/checkkeys/checkkeys.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/controllermap/controllermap.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/loopwave/loopwave.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testatomic/testatomic.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testautomation/testautomation.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testdraw2/testdraw2.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testfile/testfile.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testgamecontroller/testgamecontroller.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testgesture/testgesture.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testgl2/testgl2.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testgles2/testgles2.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testjoystick/testjoystick.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testoverlay2/testoverlay2.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testplatform/testplatform.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testpower/testpower.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testrendertarget/testrendertarget.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testrumble/testrumble.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testscale/testscale.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testsensor/testsensor.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testshape/testshape.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testsprite2/testsprite2.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testvulkan/testvulkan.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testwm2/testwm2.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/tests/testyuv/testyuv.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/visualtest/visualtest_VS2012.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC/visualtest/unittest/testquit/testquit_VS2012.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC-WinRT/tests/loopwave/loopwave_VS2012.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC-WinRT/tests/testthread/testthread_VS2012.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC-WinRT/UWP_VS2015/SDL-UWP.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC-WinRT/WinPhone81_VS2013/SDL-WinPhone81.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/SDL-src/VisualC-WinRT/WinRT81_VS2013/SDL-WinRT81.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc10/miniunz.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc10/minizip.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc10/testzlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc10/testzlibdll.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc10/zlibstat.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc10/zlibvc.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc11/miniunz.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc11/minizip.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc11/testzlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc11/testzlibdll.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc11/zlibstat.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc11/zlibvc.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc12/miniunz.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc12/minizip.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc12/testzlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc12/testzlibdll.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc12/zlibstat.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc12/zlibvc.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc14/miniunz.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc14/minizip.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc14/testzlib.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc14/testzlibdll.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc14/zlibstat.vcxproj'),
    comparablePath(f'{ ROOT_DIR }/thirdparty/zlib/contrib/vstudio/vc14/zlibvc.vcxproj'),
]


# https://lxml.de/tutorial.html
class XMLNode:
    def __init__ (self, source):
        if isinstance(source, etree._Element):
            self._node = source
        elif isinstance(source, bytes):
            self._node = etree.fromstring(source)
        else:
            raise Exception('No source. Expected bytes or XMLNode')

        self._namespaces = {
            '': self.__class__._extractNamespace(self._node)
        }

    def __str__ (self):
        return f'<{ self.__class__.__name__ } \'{ self.getTag() }\'>'

    def __repr__ (self):
        return self.__str__()

    def __len__ (self):
        return len(self._node)

    def __bool__ (self):
        return True

    @staticmethod
    def _extractNamespace (node):
        match = regex.findall(XML_NAMESPACE_REGEX, node.tag) 

        return match[0] if match else None

    def getTag (self):
        return regex.sub(XML_NAMESPACE_REGEX, '', self._node.tag) 

    def find (self, pattern):
        node = self._node.find(pattern, namespaces=self._namespaces)

        return XMLNode(node) if node is not None else None

    def findAll (self, pattern):
        nodes = self._node.findall(pattern, namespaces=self._namespaces)

        return [ XMLNode(node) for node in nodes ]

    def getText (self):
        return self._node.text

    def setText (self, text):
        self._node.text = text

    def getAttribute (self, name, default=None):
        return self._node.attrib.get(name, default)

    def getParent (self):
        return XMLNode(self._node.getparent())

    def remove (self):
        parentNode = self._node.getparent()

        if parentNode is not None:
            parentNode.remove(self._node)
            return True

        return False

    def hasChildren (self):
        return len(self._node) > 0

    def serialize (self):
        etree.indent(self._node, space='    ')
        data = etree.tostring(self._node, encoding='utf-8', xml_declaration=True, pretty_print=True)
        data = data.decode('utf-8').encode('utf-8-sig')

        return data

# Tested util functions
# ---------------------------------------------------------------------------


def getDataMD5 (data, lowerCase=True):
    checksum = hashlib.md5(data).hexdigest()

    return checksum.lower() if lowerCase else checksum.upper()


def getFileMD5 (filePath, lowerCase=True):
    assertFileExists(filePath)

    checksum = hashlib.md5()

    with open(filePath, 'rb') as f:
        while True:
            data = f.read(1024)

            if not data:
                break

            checksum.update(data)

    checksum = checksum.hexdigest()

    return checksum.lower() if lowerCase else checksum.upper()
    

def assertFileExists (filePath):
    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')


def assertDirExists (filePath):
    if not os.path.isdir(filePath):
        raise Exception(f'Directory does not exist: { filePath }')


def readBinaryFile (filePath):
    assertFileExists(filePath)

    with open(filePath, 'rb') as f:
        return f.read() 


def writeBinaryFile (filePath, data, overwrite=True):
    if os.path.isfile(filePath) and not overwrite:
        return

    if not isinstance(data, bytes):
        raise Exception(f'The data to write must be bytes: { filePath }')

    setReadOnly(filePath, False)

    with open(filePath, 'wb') as f:
        return f.write(data) 


def readTextFile (filePath, encoding='utf-8'):
    assertFileExists(filePath)

    with open(filePath, 'r', encoding=encoding) as f:
        return f.read() 


def writeTextFile (filePath, data, overwrite=True, encoding='utf-8'):
    if os.path.isfile(filePath) and not overwrite:
        return

    if not isinstance(data, str):
        raise Exception(f'The data to write must be string: { filePath }')

    setReadOnly(filePath, False)

    with open(filePath, 'w', encoding=encoding) as f:
        return f.write(data) 


def readJson (filePath, encoding='utf-8'):
    return json.loads(readTextFile(filePath, encoding=encoding).strip())


def readJsonSafe (filePath, default=None, encoding='utf-8'):
    try:
        return readJson(filePath, encoding=encoding)
    except:
        return default


def writeJson (filePath, data, pretty=True, overwrite=True, encoding='utf-8'):
    if pretty:
        indent = 4
        separators=(', ', ': ')
    else:
        indent = None
        separators=(',', ':')

    data = json.dumps(data, indent=indent, separators=separators, ensure_ascii=False)  

    writeTextFile(filePath, data, overwrite=overwrite, encoding=encoding)


def listDir (rootDir, recursive=True, filesOnly=True):
    assertDirExists(rootDir)

    rootDir = os.path.normpath(rootDir)

    if recursive:
        for baseDir, dirNames, fileNames in os.walk(rootDir):
            for item in (dirNames + fileNames):
                itemPath = os.path.join(baseDir, item)

                if not filesOnly or os.path.isfile(itemPath):
                    yield itemPath
    else:
        for item in os.listdir(rootDir):
            itemPath = os.path.join(rootDir, item)

            if not filesOnly or os.path.isfile(itemPath):
                yield itemPath


def getExtension (filePath, lowerCase=True):
    ext = os.path.splitext(filePath)[1]

    return ext.lower() if lowerCase else ext


# Tested Source-related functions
# ---------------------------------------------------------------------------


def collectInitialFiles ():
    files = []

    for filePath in listDir(SE_ROOT_DIR, True, True):
        files.append(f'{ filePath };{ getFileMD5(filePath) }')

    files.sort()

    writeJson(INITIAL_FILES_JSON_PATH, files)
    setReadOnly(INITIAL_FILES_JSON_PATH, True)

    print(f'Collected { len(files) } files')


def collectInitialVSSolutions ():
    files = []

    for filePath in listDir(SE_ROOT_DIR, True, True):
        if getExtension(filePath) in [ '.sln', '.vcxproj' ]:
            files.append(filePath)

    files.sort()

    writeJson(INITIAL_VS_SOLUTIONS_JSON_PATH, files)
    setReadOnly(INITIAL_VS_SOLUTIONS_JSON_PATH, True)

    print(f'Collected { len(files) } files')


def collectInitialLibs ():
    files = []

    for filePath in listDir(SE_ROOT_DIR, True, True):
        if getExtension(filePath) in [ '.sln', '.vcxproj' ]:
            files.append(filePath)

    files.sort()

    writeJson(INITIAL_VS_SOLUTIONS_JSON_PATH, files)
    setReadOnly(INITIAL_VS_SOLUTIONS_JSON_PATH, True)

    print(f'Collected { len(files) } files')


# Bunch of untested funcs
# ---------------------------------------------------------------------------


def splitParams (params):
    return [ param.strip() for param in params.split(';') if param.strip() ]


def parseProjectFile (projectFilePath):
    if not os.path.isfile(projectFilePath):
        print('Does not exist:', projectFilePath)
        return

    print(projectFilePath)

    with open(projectFilePath, 'rb') as f:
        rootNode = XMLNode(f.read())

    assert rootNode.getTag() == 'Project'

    # ---------------------------------------------------------------------------

    projectConfigNodes = rootNode.findAll('ItemGroup/ProjectConfiguration')

    for projectConfigNode in projectConfigNodes:
        configNode = projectConfigNode.find('Configuration')
        platformNode = projectConfigNode.find('Platform')

        assert configNode is not None
        assert platformNode is not None

        config = configNode.getText()
        platform = platformNode.getText()

        assert config in ALLOWED_BUILD_TYPES
        assert platform in ALLOWED_PLATFORMS
        assert projectConfigNode.getAttribute('Include') == f'{ config }|{ platform }'

    # ---------------------------------------------------------------------------

    exePathNodes = rootNode.findAll('PropertyGroup/ExecutablePath')

    for exePathNode in exePathNodes:
        exePaths = splitParams(exePathNode.getText())
        # TODO: modify

    # ---------------------------------------------------------------------------

    eventTypes = [ 'PreBuildEvent', 'PostBuildEvent', 'PreLinkEvent' ]
    p4editRe = regex.compile(r'^call\s*(..\\)*vpc_scripts\\valve_p4_edit\.cmd')

    for eventType in eventTypes:
        buildEventNodes = rootNode.findAll(f'ItemDefinitionGroup/{ eventType }')

        for buildEventNode in buildEventNodes:
            messageNode = buildEventNode.find('Message')
            commandNode = buildEventNode.find('Command')

            if not commandNode:
                continue

            lines = []
                 
            # Do nothing for PreBuildEvent, drop entire script
            if eventType in [ 'PostBuildEvent', 'PreLinkEvent' ]:
                for line in commandNode.getText().split('\n'):
                    line = line.strip()

                    if line and not p4editRe.match(line):
                        lines.append(line)

            command = '\n'.join(lines)
            # message = ''

            commandNode.setText(command)

            # print(command)

            if not command and messageNode: 
                messageNode.setText('')

            # message = f'{ messageNode.getText() }\n-------------------------------\n'
            # print(f'{ message }{ command }\n\n')

    # ---------------------------------------------------------------------------

    preprocDefsNodes = rootNode.findAll(f'ItemDefinitionGroup/ClCompile/PreprocessorDefinitions')

    for preprocDefsNode in preprocDefsNodes:
        params = splitParams(preprocDefsNode.getText())

        for i, param in enumerate(params):
            if param.startswith('PROJECTDIR='):
                params[i] = f'PROJECTDIR=$(ProjectDir)'  # TODO: check it works

        preprocDefsNode.setText(';'.join(params))
        

    # ---------------------------------------------------------------------------

    customBuildNodes = rootNode.findAll(f'ItemGroup/CustomBuild')

    for customBuildNode in customBuildNodes:
        messageNode = customBuildNode.find('Message')
        commandNode = customBuildNode.find('Command')
        outputsNode = customBuildNode.find('Outputs')

        if messageNode:
            # Remove entire CustomBuild for Debug and Release
            if messageNode.getText().startswith('Running VPC CRC Check'):
                customBuildNode.remove()

    # ---------------------------------------------------------------------------

    noneNodes = rootNode.findAll(f'ItemGroup/None[@Include]')

    for noneNode in noneNodes:
        if noneNode.getAttribute('Include', '').lower().endswith('.vpc'):
            parentNode = noneNode.getParent()                
            isRemoved = noneNode.remove()

            assert isRemoved

            if not parentNode.hasChildren():
                isRemoved = parentNode.remove()

                assert isRemoved

    # etree.indent(rootNode._node, space='    ')
    # data = etree.tostring(rootNode._node, encoding='utf-8', xml_declaration=True, pretty_print=True)
    # data = data.decode('utf-8').encode('utf-8-sig')

    data = rootNode.serialize()

    with open(projectFilePath, 'wb') as f:
        f.write(data)

    # print(data)
    # sys.exit(0)


def parseSolution ():
    if not os.path.isfile(SOLUTION_PATH):
        return

    def matcherProjectStart (line):
        match = PROJECT_REGEX.search(line)

        if match:
            return Project(
                match.group(1), 
                match.group(2), 
                os.path.normpath(os.path.join(ROOT_DIR, match.group(3))), 
                match.group(4), 
                []
            )

        return None

    def matcherProjectEnd (line):
        return line == 'EndProject'

    def matcherProjectDepsStart (line):
        return line.startswith('ProjectSection(ProjectDependencies)')

    def matcherProjectDepsEnd (line):
        return line == 'EndProjectSection'

    def matcherProjectDep (line):
        match = PROJECT_DEP_REGEX.search(line)

        if match:
            return ProjectDep(match.group(1), match.group(2))

        return None

    def collectProjects (lines, matchers, projects, stopMatcher):
        for line in lines:
            line = line.strip()

            for matcherStart, matcherEnd, childMatchers in matchers:
                result = matcherStart(line)

                if result:
                    if isinstance(result, Project):
                        projects.append(result)
                    elif isinstance(result, ProjectDep):
                        projects[-1].deps.append(result)

                    if childMatchers:
                        collectProjects(lines, childMatchers, projects, matcherEnd)
                elif stopMatcher and stopMatcher(line):
                    return

        return projects

    with open(SOLUTION_PATH, 'r', encoding='utf-8-sig') as f:
        lines = iter(f.readlines())

    matchers = [
        (
            matcherProjectStart, 
            matcherProjectEnd, 
            [
                (
                    matcherProjectDepsStart, 
                    matcherProjectDepsEnd, 
                    [
                        (matcherProjectDep, None, None)
                    ] 
                ),
            ]
        )
    ]

    return collectProjects(lines, matchers, [], None)


def analyzeProjects ():
    projects = parseSolution()

    for project in projects:
        filePath = project.path

        if comparablePath(filePath) in EXCLUDED_PROJECTS:
            print('Skipping:', filePath)
            continue

        parseProjectFile(filePath)


def setReadOnly (path, isReadOnly):
    if not os.path.exists(path):
        return 

    os.chmod(path, (stat.S_IREAD if isReadOnly else stat.S_IWRITE))


def setReadOnlyRecurive (rootDir, isReadOnly):
    if not os.path.isdir(rootDir):
        return

    for baseDir, dirNames, fileNames in os.walk(rootDir):
        items = dirNames + fileNames

        for item in items:
            setReadOnly(os.path.join(baseDir, item), isReadOnly)


def removeProjects ():
    projects = parseSolution()

    for project in projects:
        baseFilePath = os.path.splitext(project.path)[0]

        for ext in PROJECT_FILE_EXTS:
            filePath = baseFilePath + ext

            if os.path.isfile(filePath):
                print('Removing:', filePath)
                setReadOnly(filePath, False)
                os.remove(filePath)

def copyDLLs ():
    dlls = {}

    for item in os.listdir(GAME_BIN_DIR):
        itemPath = os.path.join(GAME_BIN_DIR, item)

        if not os.path.isfile(itemPath) or not itemPath.lower().endswith('.dll'):
            continue

        dlls[item.lower()] = [ itemPath, [] ]

    for dirName, _, fileNames in os.walk(ROOT_DIR):
        for fileName in fileNames:
            filePath = os.path.join(dirName, fileName)
            fileKey = fileName.lower()

            if not os.path.isfile(filePath) or not fileKey in dlls:
                continue

            modifiedDate = os.stat(filePath)[stat.ST_MTIME]

            dlls[fileKey][1].append((filePath, modifiedDate))

    for dllName, data in dlls.items():
        newDlls = data[1]

        if not newDlls:
            continue

        newDlls.sort(key=lambda item: item[1], reverse=True)

        newDll = newDlls[0][0]
        originalPath = data[0]
        backupPath = originalPath + '.bckp'

        if not os.path.isfile(backupPath):
            os.rename(originalPath, backupPath)
        else:
            print('Backup already exists:', backupPath)

        shutil.move(newDll, originalPath)



if __name__ == '__main__':
    pass
    # .vgc ~ .vpc
    # g_pVPC = new CVPC()  // g_pVPC->GetScript() == CScript m_Script
    # g_pVPC->GetScript().PushScript(fileName)  // parse line by line with #include
    # // /**/ "" <> [] 

    # parseProjectFiles()
    # analyzeProjects()
    # setReadOnlyRecurive(ROOT_DIR, False)
    # removeProjects()
    # copyDLLs()
    # collectInitialVSSolutions()

    # for item in listDir(os.path.join(SE_ROOT_DIR, 'linux', '..', 'linux'), False, True):
    #     print(item)
    # writeJson(os.path.join(ROOT_DIR, 'x.json'), {'data':[ 1, 2, 3 ]}, pretty=True, overwrite=True)
    # print(getFileMD5(r'G:\Steam\steamapps\common\Detroit Become Human\BigFile_PC.d01', lowerCase=False))