import os, stat, sys, regex, shutil, hashlib, json
from enum import Enum
from lxml import etree
from collections import namedtuple

from utils import *


CLI_DIR     = getDirPath(getAbsPath(__file__))
DATA_DIR    = joinPath(CLI_DIR, 'data')
PATCHES_DIR = joinPath(DATA_DIR, 'patched_files')

BEFORE_VPC_PATCH_DIR = joinPath(PATCHES_DIR, 'before_vpc')
AFTER_VPC_PATCH_DIR  = joinPath(PATCHES_DIR, 'after_vpc')

ENGINE_ROOT_DIR = r'C:\Projects\_Sources\GameEngines\SourceEngine2013_5\Source'
ROOT_SLN_PATH   = os.path.join(ENGINE_ROOT_DIR, 'everything.sln')
# BUILD_ROOT_DIR  = os.path.join(ENGINE_ROOT_DIR, '_build')
# BUILD_BIN_DIR   = os.path.join(BUILD_ROOT_DIR, 'bin')

GAME_DIR = r'G:\Steam\steamapps\common\Half-Life 2'
GAME_BIN_DIR = os.path.join(GAME_DIR, 'bin')

PROJECT_FILE_EXTS = [
    '.vcxproj',
    '.vcxproj.filters',
    '.vcxproj.user',
    '.vcxproj.vpc_crc',
]

LAUNCH_TO_MENU_DLLS = [
    'launcher.dll',
    'vstdlib.dll',
    'steam_api.dll',
    'tier0.dll',
    'FileSystem_Stdio.dll',
    'engine.dll',
    'inputsystem.dll',
    'SDL2.dll',
    'MaterialSystem.dll',
    'datacache.dll',
    'StudioRender.dll',
    'vphysics.dll',
    'video_services.dll',
    'vguimatsurface.dll',
    'vgui2.dll',
    'shaderapidx9.dll',
    'video_quicktime.dll',
    'video_bink.dll',
    'binkw32.dll',
    'stdshader_dbg.dll',
    'stdshader_dx6.dll',
    'stdshader_dx7.dll',
    'stdshader_dx8.dll',
    'stdshader_dx9.dll',
    'unicode.dll',
    'SoundEmitterSystem.dll',
    'scenefilecache.dll',
    'GameUI.dll',
    'bugreporter_filequeue.dll',
    'haptics.dll',
    'vaudio_miles.dll',
    'Mss32.dll',
    'mssmp3.asi',
    'mssvoice.asi',
    'mssdolby.flt',
    'mssds3d.flt',
    'mssdsp.flt',
    'msseax.flt',
    'msssrs.flt',
    'ServerBrowser.dll',
]

MISSING_LAUNCH_TO_MENU_DLLS = [
    'steam_api.dll',
    'SDL2.dll',
    'vphysics.dll',
    'video_bink.dll',
    'binkw32.dll',
    'haptics.dll',
    'vaudio_miles.dll',
    'Mss32.dll',
    'mssmp3.asi',
    'mssvoice.asi',
    'mssdolby.flt',
    'mssds3d.flt',
    'mssdsp.flt',
    'msseax.flt',
    'msssrs.flt',
]


#----------------------------------------------------------------------


def readFileLines (filePath, encoding='utf-8'):
    with open(filePath, 'r', encoding=encoding) as f:
        return f.readlines()


def setReadOnlyRecursive (rootDir, isReadOnly):
    if not os.path.isdir(rootDir):
        return

    for baseDir, dirNames, fileNames in os.walk(rootDir):
        items = dirNames + fileNames

        for item in items:
            setReadOnly(os.path.join(baseDir, item), isReadOnly)


def collectInitialLibs ():
    files = []

    for filePath in listDir(ENGINE_ROOT_DIR, True, True):
        if getExtension(filePath) == '.lib':
            files.append(f'{ filePath };{ getFileMD5(filePath) }')

    files.sort()

    writeJson(INITIAL_LIBS_JSON_PATH, files)
    setReadOnly(INITIAL_LIBS_JSON_PATH, True)

    print(f'Collected { len(files) } files')


class Project:
    def __init__ (self, typeId, name, relPath, id):
        self.typeId = typeId
        self.name = name
        self.filePath = relPath
        self.id = id
        self.deps = []
        self.allDeps = []

    def __str__ (self):
        return self.name

    def __repr__ (self):
        return self.name


class DependencyNode:
    pattern = regex.compile(r'^\{([^\}]+)\}\s*=.*\}$')
    closeTag = None
    child = None


class DependenciesNode:
    pattern = regex.compile(r'^ProjectSection\(ProjectDependencies\)\s*=\s*postProject$')
    closeTag = 'EndProjectSection'
    child = DependencyNode


class ProjectNode:
    pattern = regex.compile(r'^Project\("\{([^\}]+)\}"\)\s*=\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"\{([^\}]+)\}"$')
    closeTag = 'EndProject'
    child = DependenciesNode


class RootNode:
    pattern = None
    closeTag = None
    child = ProjectNode


def readTree (lines, parent, projects):
    for line in lines:
        if line == parent.closeTag:
            break

        match = parent.child.pattern.search(line)

        if not match:
            continue 

        if parent.child == ProjectNode:
            projects.append(Project(*match.groups()))
        elif projects and parent.child == DependencyNode:
            projects[-1].deps.append(match.group(1))

        if parent.child.child:
            readTree(lines, parent.child, projects)

    return projects


def getSolutionProjects (slnPath):
    slnPath = os.path.normpath(slnPath)
    slnDir = os.path.dirname(slnPath)
    lines = [ line.strip() for line in readFileLines(slnPath, 'utf-8-sig') if line.strip() ]
    lines = iter(lines[4:])  # skip header lines
    projects = readTree(lines, RootNode, [])
    projectMap = {}

    for project in projects:
        project.filePath = os.path.normpath(os.path.join(slnDir, project.filePath))
        projectMap[project.id] = project

    def findDeps (deps, rootProject):
        for depId in deps:
            depProject = projectMap[depId]

            if depProject.id not in rootProject.allDeps:
                rootProject.allDeps.append(depProject.id)
                findDeps(depProject.deps, rootProject)

    for project in projects:
        findDeps(project.deps, project)

        # print(f'{ project.name }:')
        # for dep in project.allDeps:
        #     print('-', dep.name)
        # print('\n')

    return projects


def showSolutionProjects (slnPath):
    for project in getSolutionProjects(slnPath):
        print(project.name + ':')

        for dep in project.allDeps:
            print('- ' + dep.name)

        print(' ')


#----------------------------------------------------------------------


XML_NAMESPACE_REGEX = regex.compile(r'^\{([^\}]+)\}')
ALLOWED_BUILD_TYPES = [ 'Debug', 'Release' ]
ALLOWED_PLATFORMS = [ 'Win32' ]
PATH_SPLIT_REGEX = regex.compile(r'[\\\/]+')
# MACROS_REGEX = regex.compile(r'^[\$%]\([^\)]+\)$')
# MACROS_PATH_SPLIT_REGEX = regex.compile(r'(?:[\\\/]+|([\$%]\([^\)]+\)))')


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
        return self._node.text or ''

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


def splitNonEmpty (string, sep):
    return [ comp.strip() for comp in string.split(sep) if comp.strip() ]


def joinNonEmpty (comps, sep):
    return sep.join([ comp.strip() for comp in comps if comp.strip() ])


def splitPath (path):
    return [ comp.strip() for comp in PATH_SPLIT_REGEX.split(path) if comp.strip() ]


def canBeRelativePath (path):
    if not isinstance(path, str):
        return False

    path = path.strip()

    if isAbsPath(path):
        return False

    return not regex.match(r'^[\$%]\([^\)]*(Path|Dir)[^\)]*\)', path.strip())


def modifyResourcePath (relPath, projDir, rootDir, macros, addSlash):
    absPath = os.path.normpath(os.path.join(projDir, relPath))
    slnRelPath = macros + os.path.relpath(absPath, rootDir)

    if addSlash:
        slnRelPath += os.path.sep

    return slnRelPath


def normScriptPath (path, projDir, rootDir, macros):
    path = path.replace('"', '')

    if canBeRelativePath(path):
        path = modifyResourcePath(path, projDir, rootDir, macros, False)
        path = path.replace(f'{ macros }..\\game\\', f'{ macros }_build\\')

    path = '"' + path + '"'

    return path


def extractCopyCmd (line, cmd, pathCount, projDir, rootDir, macros):
    if pathCount == 1:
        regexStr = rf'(?:^|\s)(?:{ cmd })\s+((?:[^:\*\?"<>\|\s]+|(?:"[^:\*\?"<>\|]*"))+)'
    elif pathCount == 2:
        regexStr = rf'(?:^|\s)(?:{ cmd })\s+((?:[^:\*\?"<>\|\s]+|(?:"[^:\*\?"<>\|]*"))+)\s+((?:[^:\*\?"<>\|\s]+|(?:"[^:\*\?"<>\|]*"))+)'
    else:
        raise Exception('Expected pathCount == 1 or 2')

    parts = []
    lastEnd = 0

    for match in regex.finditer(regexStr, line, flags=regex.I):
        if pathCount == 1:
            paths = normScriptPath(match.group(1), projDir, rootDir, macros)
            matchStart = match.span(1)[0]
            matchEnd = match.span(1)[1]
            # print(matchStart, matchEnd)
        elif pathCount == 2:
            path1 = normScriptPath(match.group(1), projDir, rootDir, macros)
            path2 = normScriptPath(match.group(2), projDir, rootDir, macros)
            paths = path1 + ' ' + path2
            matchStart = match.span(1)[0]
            matchEnd = match.span(2)[1]

        parts.append(line[lastEnd:matchStart])
        parts.append(paths)

        lastEnd = matchEnd

    parts.append(line[lastEnd:len(line)])

    return ''.join(parts)     


def normalizeProjectFilters (filtersFilePath, rootDir):
    if not os.path.isfile(filtersFilePath):
        return

    with open(filtersFilePath, 'rb') as f:
        rootNode = XMLNode(f.read())

    assert rootNode.getTag() == 'Project'

    selectors = [ 'ItemGroup/None[@Include]', 'ItemGroup/CustomBuild[@Include]' ]

    for selector in selectors:
        for noneNode in rootNode.findAll(selector):
            if not noneNode.getAttribute('Include', '').lower().endswith('.vpc'):
                continue

            filterNode = noneNode.find('Filter')

            assert filterNode

            filterName = filterNode.getText().strip()

            if filterName:
                filterNode = rootNode.find(f'ItemGroup/Filter[@Include=\'{ filterName }\']')

                if filterNode:
                    parentNode = filterNode.getParent()  
                    isRemoved = filterNode.remove()

                    assert isRemoved

            parentNode = noneNode.getParent()                
            isRemoved = noneNode.remove()

            assert isRemoved

            if not parentNode.hasChildren():
                isRemoved = parentNode.remove()

                assert isRemoved

    data = rootNode.serialize()

    with open(filtersFilePath, 'wb') as f:
        f.write(data)


def normalizeProject (projectFilePath, rootDir):
    if not os.path.isfile(projectFilePath):
        print('Does not exist:', projectFilePath)
        return

    projectDir = os.path.dirname(projectFilePath)

    # print(projectFilePath)

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

    selectors = [
        ('PropertyGroup/ExecutablePath', True),
        ('ItemDefinitionGroup/ClCompile/AdditionalIncludeDirectories', True),
        ('ItemDefinitionGroup/Link/AdditionalLibraryDirectories', True),
        ('ItemDefinitionGroup/Link/AdditionalDependencies', False)
    ]

    throwDeps = [
        'xgraphics.lib',
        'xmaencoder.lib',
        'legacy_stdio_definitions.lib'
    ]

    for selector, addSlash in selectors:
        isDeps = selector == 'ItemDefinitionGroup/Link/AdditionalDependencies'

        for pathNode in rootNode.findAll(selector):
            paths = splitNonEmpty(pathNode.getText(), ';')
            newPaths = []

            for path in paths:
                if isDeps and (path.lower() in throwDeps):
                    continue

                if canBeRelativePath(path) and (not isDeps or regex.search(r'[\\\/]', path)):
                    path = regex.sub(r'(thirdparty[\\\/]+fbx[\\\/]+FbxSdk[\\\/]+2015\.1[\\\/]+lib[\\\/]+)vs2012([\\\/]+x86[\\\/]+release[\\\/]+libfbxsdk\.lib)$', r'\1vs2013\2', path, flags=regex.I)
                    # path = modifyResourcePath(path, projectDir, rootDir, '$(SolutionDir)', addSlash)

                newPaths.append(path)

            pathNode.setText(joinNonEmpty(newPaths, ';'))

    # ---------------------------------------------------------------------------

    extraWarnings = [ 4100, 4125, 4127, 4244, 4512, 4530 ]

    for pathNode in rootNode.findAll('ItemDefinitionGroup/ClCompile/DisableSpecificWarnings'):
        warnings = [ int(warn) for warn in splitNonEmpty(pathNode.getText(), ';') ]
        warnings = [ str(warn) for warn in sorted(list(set(warnings + extraWarnings))) ]

        pathNode.setText(';'.join(warnings))  

        print(warnings)  

    # ---------------------------------------------------------------------------

    # selectors = [
    #     ('PropertyGroup/OutDir', True),
    #     ('PropertyGroup/IntDir', True),
    #     ('ItemDefinitionGroup/Lib/OutputFile', False)
    # ]

    # for selector, addSlash in selectors:
    #     for pathNode in rootNode.findAll(selector):
    #         path = pathNode.getText()

    #         if canBeRelativePath(path):
    #             pathNode.setText(modifyResourcePath(path, projectDir, rootDir, '$(SolutionDir)', addSlash))
    #             # print(selector, path, pathNode.getText())

    # ---------------------------------------------------------------------------

    # The lib path must always be relative, so don't modify it 
    # for libNode in rootNode.findAll('ItemDefinitionGroup/Link/ImportLibrary'):
    #     libNode.setText(modifyResourcePath(libNode.getText(), projectDir, rootDir, '$(SolutionDir)', False))        

    # ---------------------------------------------------------------------------

    for libNode in rootNode.findAll('ItemGroup/Library'):
        libName = os.path.basename(libNode.getAttribute('Include', ''))

        # telemetry32.link.lib is not found anywhere
        # Remove it from deps and add RAD_TELEMETRY_DISABLED to preproc defs (below)
        if libName.lower() == 'telemetry32.link.lib':
            libNode.remove()

    # ---------------------------------------------------------------------------

    '''
    eventTypes = [ 'PreBuildEvent', 'PostBuildEvent', 'PreLinkEvent' ]
    p4editRe = regex.compile(r'^call\s*(..\\)*vpc_scripts\\valve_p4_edit\.cmd')
    newdatRe = regex.compile(r'^(..\\)*game.*bin[\\\/]+newdat\s*(..\\)*game.*[\\\/]+hl2\.exe')

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

                    if not line or p4editRe.match(line) or newdatRe.match(line):
                        continue

                    line = extractCopyCmd(line, 'copy', 2, projectDir, rootDir, '$(SolutionDir)')
                    line = extractCopyCmd(line, 'exist|mkdir', 1, projectDir, rootDir, '$(SolutionDir)')

                    lines.append(line)

            command = '\n'.join(lines)
            # message = ''

            commandNode.setText(command)

            # if eventType == 'PostBuildEvent': # and ('..' in command):
            #     print(command, '\n\n')

            if not command and messageNode: 
                messageNode.setText('')

            # message = f'{ messageNode.getText() }\n-------------------------------\n'
            # print(f'{ message }{ command }\n\n')
    '''

    # ---------------------------------------------------------------------------

    preprocDefsNodes = rootNode.findAll('ItemDefinitionGroup/ClCompile/PreprocessorDefinitions')

    for preprocDefsNode in preprocDefsNodes:
        params = splitNonEmpty(preprocDefsNode.getText(), ';')

        for i, param in enumerate(params):
            if param.startswith('PROJECTDIR='):
                # Throw trailing slash otherwise preproc cmd line arg will be invalid
                params[i] = r"PROJECTDIR=$(ProjectDir.TrimEnd('\'))"  
                break

        definitions = [
            # 'NO_STEAM',             # Standalone build w/o Steam integration; DON'T USE: it breaks steam-related legacy code
            'NO_X360_XDK',            # Forget X360 forever
            'RAD_TELEMETRY_DISABLED'  # Disable RAD Game Tools Telemetry coz .lib not found
        ]

        for definition in definitions:
            if definition not in params:
                # Add to the beginning coz for some reason it doesn't work when at the end
                params.insert(0, definition)

        preprocDefsNode.setText(joinNonEmpty(params, ';'))        

    # ---------------------------------------------------------------------------

    customBuildNodes = rootNode.findAll('ItemGroup/CustomBuild')

    for customBuildNode in customBuildNodes:
        messageNode = customBuildNode.find('Message')
        commandNode = customBuildNode.find('Command')
        outputsNode = customBuildNode.find('Outputs')

        if messageNode:
            # Remove entire CustomBuild for Debug and Release
            if messageNode.getText().startswith('Running VPC CRC Check'):
                customBuildNode.remove()
            # print(messageNode.getText())

    # ---------------------------------------------------------------------------

    noneNodes = rootNode.findAll('ItemGroup/None[@Include]')

    for noneNode in noneNodes:
        if noneNode.getAttribute('Include', '').lower().endswith('.vpc'):
            parentNode = noneNode.getParent()                
            isRemoved = noneNode.remove()

            assert isRemoved

            if not parentNode.hasChildren():
                isRemoved = parentNode.remove()

                assert isRemoved

    # ---------------------------------------------------------------------------

    data = rootNode.serialize()

    normalizeProjectFilters(projectFilePath + '.filters', rootDir)

    # print(data.decode('utf-8-sig'))

    with open(projectFilePath, 'wb') as f:
        f.write(data)


def patchProject (projectFilePath, rootDir):
    if not os.path.isfile(projectFilePath):
        print('Does not exist:', projectFilePath)
        return

    projectDir = os.path.dirname(projectFilePath)

    # print(projectFilePath)

    with open(projectFilePath, 'rb') as f:
        rootNode = XMLNode(f.read())

    assert rootNode.getTag() == 'Project'

    # Drop legacy lib-deps and patch paths
    # ---------------------------------------------------------------------------

    selectors = [
        ('PropertyGroup/ExecutablePath', True),
        ('ItemDefinitionGroup/ClCompile/AdditionalIncludeDirectories', True),
        ('ItemDefinitionGroup/Link/AdditionalLibraryDirectories', True),
        ('ItemDefinitionGroup/Link/AdditionalDependencies', False)
    ]

    depsToDrop = [
        'xgraphics.lib',
        'xmaencoder.lib',
        'legacy_stdio_definitions.lib'
    ]

    for selector, addSlash in selectors:
        isDeps = selector == 'ItemDefinitionGroup/Link/AdditionalDependencies'

        for pathNode in rootNode.findAll(selector):
            paths = splitNonEmpty(pathNode.getText(), ';')
            newPaths = []

            for path in paths:
                if isDeps and (path.lower() in depsToDrop):
                    continue

                if canBeRelativePath(path) and (not isDeps or regex.search(r'[\\\/]', path)):
                    path = regex.sub(r'(thirdparty[\\\/]+fbx[\\\/]+FbxSdk[\\\/]+2015\.1[\\\/]+lib[\\\/]+)vs2012([\\\/]+x86[\\\/]+release[\\\/]+libfbxsdk\.lib)$', r'\1vs2013\2', path, flags=regex.I)
                    # path = modifyResourcePath(path, projectDir, rootDir, '$(SolutionDir)', addSlash)

                newPaths.append(path)

            pathNode.setText(joinNonEmpty(newPaths, ';'))

    # Suppress some warnings
    # ---------------------------------------------------------------------------

    extraWarnings = [ 4100, 4125, 4127, 4244, 4512, 4530, 4701, 4703 ]

    for pathNode in rootNode.findAll('ItemDefinitionGroup/ClCompile/DisableSpecificWarnings'):
        warnings = [ int(warn) for warn in splitNonEmpty(pathNode.getText(), ';') ]
        warnings = [ str(warn) for warn in sorted(list(set(warnings + extraWarnings))) ]

        pathNode.setText(';'.join(warnings))

    # Drop Telemetry dep
    # ---------------------------------------------------------------------------

    for libNode in rootNode.findAll('ItemGroup/Library'):
        libName = os.path.basename(libNode.getAttribute('Include', ''))

        # telemetry32.link.lib is not found anywhere
        # Remove it from deps and add RAD_TELEMETRY_DISABLED to preproc defs (below)
        if libName.lower() == 'telemetry32.link.lib':
            libNode.remove()

    # Patch preprocessor definitions
    # ---------------------------------------------------------------------------

    preprocDefsNodes = rootNode.findAll('ItemDefinitionGroup/ClCompile/PreprocessorDefinitions')

    for preprocDefsNode in preprocDefsNodes:
        params = splitNonEmpty(preprocDefsNode.getText(), ';')

        # for i, param in enumerate(params):
        #     if param.startswith('PROJECTDIR='):
        #         # Throw trailing slash otherwise preproc cmd line arg will be invalid
        #         params[i] = r"PROJECTDIR=$(ProjectDir.TrimEnd('\'))"  
        #         break

        definitions = [
            # 'NO_STEAM',             # Standalone build w/o Steam integration; DON'T USE: it breaks steam-related legacy code
            'NO_X360_XDK',            # Forget X360 forever
            'RAD_TELEMETRY_DISABLED'  # Disable RAD Game Tools Telemetry coz .lib not found
        ]

        for definition in definitions:
            if definition not in params:
                # Add to the beginning coz for some reason it doesn't work when at the end
                params.insert(0, definition)

        preprocDefsNode.setText(joinNonEmpty(params, ';')) 

    # Patch build events
    # ---------------------------------------------------------------------------

    # eventTypes = [ 'PreBuildEvent', 'PostBuildEvent', 'PreLinkEvent' ]

    # for eventType in eventTypes:
    #     buildEventNodes = rootNode.findAll(f'ItemDefinitionGroup/{ eventType }')

    #     for buildEventNode in buildEventNodes:
    #         buildEventNode.remove()

    # Remove VPCs from project's file list
    # ---------------------------------------------------------------------------

    noneNodes = rootNode.findAll('ItemGroup/None[@Include]')

    for noneNode in noneNodes:
        if noneNode.getAttribute('Include', '').lower().endswith('.vpc'):
            parentNode = noneNode.getParent()                
            isRemoved = noneNode.remove()

            assert isRemoved

            if not parentNode.hasChildren():
                isRemoved = parentNode.remove()

                assert isRemoved  

    # ---------------------------------------------------------------------------

    data = rootNode.serialize()

    normalizeProjectFilters(projectFilePath + '.filters', rootDir)

    with open(projectFilePath, 'wb') as f:
        f.write(data)


def patchProjects (slnPath):
    projects = getSolutionProjects(slnPath)

    print(len(projects), 'projects found')

    for project in projects:
        # normalizeProject(project.filePath, os.path.dirname(slnPath))
        patchProject(project.filePath, os.path.dirname(slnPath))
        #break


def postVPC (slnPath):
    rootDir = os.path.dirname(slnPath)

    print('Patching projects...')
    patchProjects(slnPath)

    # print('Making all files writable...')
    # setReadOnlyRecursive(rootDir, False)

    print('Done')


def preVPC (rootDir):
    if not isDir(rootDir):
        print(f'Dest dir does not exist: { rootDir }')
        return

    if not isDir(BEFORE_VPC_PATCH_DIR):
        print('No patches')
        return

    print('Patching files...\n')

    rootDir = getAbsPath(rootDir)

    for srcPath in iterFiles(BEFORE_VPC_PATCH_DIR):
        relPath  = getRelPath(srcPath, BEFORE_VPC_PATCH_DIR)
        destPath = joinPath(rootDir, relPath)
        destDir  = getDirPath(destPath)

        print(getRelPath(destPath, rootDir))

        createDirs(destDir)

        if isFile(destPath):
            wasReadOnly = checkReadOnly(destPath)
            setReadOnly(destPath, False)
        else:
            wasReadOnly = False

        shutil.copyfile(srcPath, destPath)

        setReadOnly(destPath, wasReadOnly)

    print('\nDone')


def _copy ():
    files = [
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\game\shared\gcschema_portal.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\game\shared\schema_cstrike.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\game\shared\schema_tf.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\launcher_main\launcher_main.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\tier0\tier0.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\togl\togl.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\unitlib\unitlib.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\utils\itemtest\itemtest_com.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\utils\simdtest\simdtest.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\utils\videocardstats\cardstats.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\protobuf_builder.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_dll_win32_base.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_dll_win32_debug.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_dll_win32_release.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_dll_x360_base.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_dll_x360_debug.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_dll_x360_release.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_exe_win_win32_base.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_exe_win_win32_debug.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_exe_win_win32_release.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_lib_win32_base.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_lib_win32_debug.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_lib_win32_release.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_lib_x360_base.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_lib_x360_debug.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_lib_x360_release.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_xex_x360_base.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_xex_x360_debug.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\source_xex_x360_release.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vpc_scripts\swig_python.vpc',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_4\Source\vstdlib\vstdlib.vpc',
    ]

    for srcPath in files:
        relPath = getRelPath(srcPath, ENGINE_ROOT_DIR)
        destPath = joinPath(BEFORE_VPC_PATCH_DIR, relPath)

        createDirs(getDirPath(destPath))

        shutil.copyfile(srcPath, destPath)

        setReadOnly(destPath, False)




#----------------------------------------------------------------------


def findStrings (data):
    results = []

    if not data:
        return results

    dataSize = len(data)
    startPos = 0
    chunk = ''

    for i in range(dataSize):
        byte   = data[i]
        isChar = 32 < byte <= 126

        if isChar:
            chunk += chr(byte)
        
        if (not isChar or (dataSize - i) == 1) and len(chunk) >= 5:
            results.append(chunk)
            chunk = ''

    return results


def findDLLNames (data, moduleNames):
    result  = []
    strings = findStrings(data)

    for string in strings:
        match = regex.search(r'([a-z\d_\.\-]+)\.dll$', string, flags=regex.I)

        if not match:
            continue

        string = match.group(1).lower()

        for moduleName in moduleNames:
            if string.endswith(moduleName) and moduleName not in result:
                result.append(moduleName)

    return sorted(result)


def collectDLLs (rootDir):
    moduleMap = {
        getFileName(modulePath).lower(): modulePath
        for modulePath in iterFiles(rootDir, includeExts=[ '.dll' ])
    }

    return moduleMap


def scanDLLs ():
    rootDir = getAbsPath(r'C:\Projects\_Sources\GameEngines\SourceEngine2013_3\Content\_bin')
    moduleMap = collectDLLs(rootDir)
    moduleNames = sorted(moduleMap.keys(), key=lambda item: len(item), reverse=True)

    queue  = [ joinPath(rootDir, 'hl2.exe') ]
    depMap = {}

    while len(queue):
        modulePath = queue.pop().lower()
        moduleName = getFileName(modulePath)

        print('Scanning', modulePath)

        with open(modulePath, 'rb') as f:
            data = f.read()

        depNames = findDLLNames(data, moduleNames)

        depMap[moduleName] = []

        for depName in depNames:
            if moduleName == depName:
                continue

            depMap[moduleName].append(depName)

            depPath = moduleMap[depName]

            if depName not in depMap and depPath not in queue:
                queue.append(depPath)

    # depMap = sorted(depMap.items(), key=lambda item: item[0])

    # for moduleName, modulePath in depMap:
    #     print(moduleName, modulePath)

    # for depName in sorted(list(set(sum(depMap.values(), [])))):
    #     print(depName)

    return depMap


def collectDeps ():
    modToProjMap = {}
    modToProjNameMap = {
        'client': 'client (hl2)',
        'server': 'server (hl2)',
        'hl2':    'launcher_main'
    }

    depMap = scanDLLs()
    projects = getSolutionProjects(ROOT_SLN_PATH)
    projectMap = { project.id: project for project in projects }

    # for project in projects:
    #     print(project.name + ':')

    #     for depId in project.allDeps:
    #         print('- ' + projectMap[depId].name)

    #     print(' ')

    moduleNames = list(set(sum(list(depMap.values()), list(depMap.keys()))))

    for moduleName in moduleNames:
        projectName = modToProjNameMap.get(moduleName, moduleName)
        isFound = False

        for project in projects:
            if project.name.lower() == projectName:
                modToProjMap[moduleName] = project
                isFound = True

                break

        if not isFound:
            print('Not found:', moduleName, projectName)

    for moduleName, moduleDeps in depMap.items():
        moduleProject = modToProjMap.get(moduleName)

        if not moduleProject:
            continue

        for moduleDep in moduleDeps:
            depProject = modToProjMap.get(moduleDep)

            if not depProject:
                continue

            if depProject.id not in moduleProject.deps:
                moduleProject.deps.append(depProject.id)

                print(f'Adding project "{ depProject.name }" (module "{ moduleDep }") to project "{ moduleProject.name }" deps')

    def findDeps (deps, rootProject):
        for depId in deps:
            depProject = projectMap[depId]

            if depProject.id not in rootProject.allDeps:
                # print(depProject.name, 'to', rootProject.name)
                rootProject.allDeps.append(depProject.id)
                findDeps(depProject.deps, rootProject)

    for project in projects:
        findDeps(project.deps, project)

    # for project in projects:
    #     if project.name != 'launcher_main':
    #         continue

    #     print(project.name + ':')

    #     for depId in project.allDeps:
    #         print('- ' + projectMap[depId].name)

    #     print(' ')

    launcherProject = None

    for project in projects:
        if project.name == 'launcher_main':
            launcherProject = project
            break

    assert launcherProject

    hl2Projects = [ project for project in projects if project == launcherProject or project.id in launcherProject.allDeps ]
    resolved = {}
    level = 0

    while len(resolved) != len(hl2Projects):
        levelResolved = {}

        for project in hl2Projects:
            if project.id in resolved:
                continue

            areDepsResolved = True

            for depId in project.allDeps:
                depProject = projectMap[depId]

                if depProject.id not in resolved:
                    areDepsResolved = False
                    break

            if areDepsResolved:
                levelResolved[project.id] = level

        resolved |= levelResolved
        level += 1

    groups = [ [] for _ in range(level) ]

    for projectId, level in resolved.items():
        groups[level].append(projectMap[projectId])

    for i, groupProjects in enumerate(groups):
        print('Level', i)

        groupProjects = sorted(groupProjects, key=lambda item: item.name)

        for project in groupProjects:
            print('-', project.name)

        print(' ')


def modifyVPCScripts ():
    count = 0

    for vpcPath in iterFiles(BEFORE_VPC_PATCH_DIR, includeExts=['.vpc']):
        with open(vpcPath, 'r', encoding='utf-8') as f:
            data = f.read()  # 180

        # '$Macro OUTBINDIR    "$SRCDIR\..\game\bin"'
        # match = regex.search(r'\$Macro\s+OUTBINDIR\s+"[^"]*\.\.\\(game)("|\\[^"]*")', data, flags=regex.I)

        newData = regex.sub(r'(.*\$Macro\s+OUTBINDIR\s+"[^"]*\.\.\\)(game)((?:"|\\[^"]*").*)', r'\1Content\3', data)

        if data != newData:
            setReadOnly(vpcPath, False)

            with open(vpcPath, 'w', encoding='utf-8') as f:
                f.write(newData)

            count += 1

        print(count, vpcPath)



if __name__ == '__main__':
    # preVPC(ENGINE_ROOT_DIR)
    # postVPC(ROOT_SLN_PATH)

    # for project in getSolutionProjects(ROOT_SLN_PATH):
    #     if project.name not in [ 'vphysics' ]:
    #         continue

    #     print(project.name + ':')

    #     for dep in project.allDeps:
    #         print('- ' + dep.name)

    exs = [ getFileName(existPath).lower() for existPath in iterFiles(r'C:\Projects\_Sources\GameEngines\SourceEngine2013_5\Content\bin', False, includeExts=[ '.dll' ]) ]
    req = [ getFileName(existPath).lower() for existPath in iterFiles(r'C:\Projects\_Sources\GameEngines\SourceEngine2013_5\Content\bin\bin', False, includeExts=[ '.dll' ]) ]

    for item in sorted(list(set(req) - set(exs))):
        print(item)

    # scanDLLs()
    # collectDeps()

    # modifyVPCScripts()

    '''
    - preVPC
    - Copy /ivp and copy everything from ivp/havana/havok/hk_physics to ivp/ivp_physics/hk_physics WITHOUT replacement
    - Copy /thirdparty/zlib-1.2.5
    - Copy /dx9sdk and /dx10sdk from SE2011
    - Copy /thirdparty/SDL2 for inputsystem
    - Copy /thirdparty/protobuf-2.6.1 for Client (HL2) (dir /bin/win32 is absent)
    - Copy /lib/common/binkw32.lib from SE2011
    - createallprojects.bat
    - postVPC

    https://developer.valvesoftware.com/wiki/Command_Line_Options

    -----------------------------------

    Level 0
    + Bzip2 (lib)
    + Dmxloader (lib)
    + appframework (lib)
    + bitmap (lib)
    + choreoobjects (lib)
    + havana_constraints (lib)
    + hk_base (lib)
    + hk_math (lib)
    + ivp_compactbuilder (lib)
    + ivp_physics (lib)
    + lzma (lib)
    + mathlib (lib)
    + particles (lib)
    + replay_common (lib)
    + shaderlib (lib)
    + tier0 (dll)
    + tier1 (lib)
    + tier2 (lib)
    + tier3 (lib)
    + vgui_controls (lib)
    + vgui_surfacelib (lib)
    + vpklib (lib)
    + vtf (lib)
    + zlib (lib)
     
    Level 1
    + matsys_controls (lib)
    + vstdlib (lib)
     
    Level 2
    + FileSystem_Stdio (dll)
    + GameUI (dll)
    + Newdat (dll) (remove?)
    + SceneFileCache (dll)
    + SoundEmitterSystem (dll)
    + StudioRender (dll)
    + Unicode (dll)
    + datacache (dll)
    + inputsystem (dll)
    + replay (dll)
    + shaderapiempty (dll)
    + stdshader_dbg (dll)
    + stdshader_dx6 (dll) (added)
    + stdshader_dx7 (dll) (added)
    + stdshader_dx8 (dll) (added)
    + stdshader_dx9 (dll) (added)
    + vgui2 (dll)
    + vguimatsurface (dll)
    + video_services (dll)
    + vphysics (dll)
     
    Level 3
    + Client (HL2) (dll)
    + MaterialSystem (dll)
    + Server (HL2)
    + SourceVR (dll)
    + Vtex_dll (dll)
    + bsppack (dll)
     
    Level 4
    + engine (dll)
    + shaderapidx9 (dll)
     
    Level 5
    + launcher (dll)
     
    Level 6
    + launcher_main (exe)

    Manual
    + tools/commedit (dll) 
    + tools/pet (dll) 
    + tools/vmt (dll) 
    + adminserver (dll) 
    + bugreporter (dll) 
    + bugreporter_filequeue (dll) 
    + bugreporter_public (dll) 
    + bugreporter_text (dll) 
    + datamodel (lib)
    + dmserializers (lib)
    + filesystemopendialog (dll) 
    + hammer_dll (dll)
    + mdllib (dll)
    + mysql_wrapper (dll)
    + serverplugin_empty (dll)
    + serverbrowser (dll)
    + shadercompile_dll (dll)
    + soundsystem (dll)
    + texturecompile_dll (dll)
    + unitlib (dll)
    + vaudio_speex (dll)
    + video_quicktime (dll)
    + vrad_dll (dll)
    + vvis_dll (dll)

    -----------------------------------

    JUST COPY:  // copy from .misc
    - avcodec-53
    - avformat-53
    - avutil-51
    - binkw32
    - chromehtml
    - haptics
    - icudt
    - icudt42
    - libcef
    - libfbxsdk
    - libsasl
    - mss32
    - msvcr71
    - parsifal
    - sdl2
    - steam_api
    - telemetry32
    - unicows
    - valvedeviceapi
    - vtex
    - xinput1_3

    UNKNOWN:
    - phonemeextractor/ims_helper
    - phonemeextractor/phonemeextractor
    - phonemeextractor/phonemeextractor_ims
    - sixense
    - sixense_utils
    - vaudio_miles
    - video_bink

    DLL DEPS:  // output of collectDeps
    - bsppack
    - client
    - datacache
    - engine
    - filesystem_stdio
    - gameui
    - haptics
    - inputsystem
    - launcher
    - materialsystem
    - mss32
    - replay
    - scenefilecache
    - sdl2
    - server
    - shaderapidx9
    - shaderapiempty
    - soundemittersystem
    - sourcevr
    - stdshader_dbg
    - steam_api
    - studiorender
    - telemetry32
    - tier0
    - unicode
    - vgui2
    - vguimatsurface
    - video_services
    - vphysics
    - vstdlib
    - vtex_dll
    '''


    # showSolutionProjects(ROOT_SLN_PATH)
    # collectInitialLibs()
    # print(_tmp['count'])
    
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


# - copy valve_p4_edit.cmd from 2007
# - patch groups.vgc
# - patch post-build and pre-build events in vpcs ???
# - patch tf extra file in vpc
# - patch createprojects.bat
# - deps, dxXsdk
# - run createprojects.bat
# - patch projects with cli

# TODO:
# - Remove DXProxy X360


'''
Todo:
- Create/find dlls:
  - steam_api.dll  NEEDED_FOR_LAUNCH_TO_MENU
  - SDL2.dll       NEEDED_FOR_LAUNCH_TO_MENU
  - vphysics.dll   NEEDED_FOR_LAUNCH_TO_MENU
  - video_bink.dll
  - binkw32.dll
  - haptics.dll
  - vaudio_miles.dll
  - Mss32.dll
  - mssmp3.asi
  - mssvoice.asi
  - mssdolby.flt
  - mssds3d.flt
  - mssdsp.flt
  - msseax.flt
  - msssrs.flt

Notes:
- 

History:
- Added FBXSDK 2015.1 to thirdparty/fbx
- Copied /vpc_scripts/fbx.vpc & fbx_base.vpc from SourceEngine2011 to SourceEngine2013_2
- Copied /utils/fbx2dmx from SourceEngine2011
- Copied /fbxutils from SourceEngine2011
- Downloaded and added /ivp for havana_constraints.vpc
- Copied /utils/phonemeextractor and /public/phonemeextractor/phonemeextractor.h from SourceSDK2013
- Added macro OUTDLLEXT to vpc_scripts/source_dll_win32_base.vpc
- Copied engine/voice_codecs/miles from 2011 (found lib, no src; also found src in 2007 & 2011)
- Copied /thirdparty/zlib-1.2.5 from 2011
- Copied /dx9sdk from 2011
- Copied /common/Miles/mss.h from 2007 and /lib/common/mss32.lib from 2011 (nothing found in 2013)
- Copied from all files from /ivp/havana/havok/hk_physics to /ivp/ivp_physics/hk_physics (original files in !original_files.zip)
- Copied /public/maya/* from 2011 for hammer_dll.vpc
- Copied /utils/bugreporter/trktool.h and /lib/common/trktooln.lib from 2007 for getbugs.vpc, bugreporter.vpc, bugreporter_text.vpc, bugreporter_text.vpc
- Copied /public/(fbxutils|fbxsystem)/* and /lib/public/fbxutils.lib from 2011 for fbxutils.vpc
- Downloaded and added most of /thirdparty
- In projects.vgc commented out non-existing vpcs:
    - socketlib.vpc (lib & includes found in /public and /lib/public)
    - haptics.vpc (found h/cpp in /public/haptics, may be these are sources?)
    - ifm.vpc (no h/cpp/lib/vpc)
    - lua.vpc (found h/cpp/lib, no vpc)
    - lxVsDmxIO_modo302.vpc (nothing found)
    - p4lib.vpc (found everything, but not needed I think)
    - sdktoolslib.vpc (found h/cpp/lib, no vpc)
    - everything in /sdktools/(valveMaya|valvePython) (no vpcs; for python found lib; for maya found ?sdktoolslib?)
    - video_bink.vpc (found nothin; there is /lib/common/win32/2015/release/binkw32.lib)
    - vp_python2.5.vpc (found only lib/common/python/2.5/python25.lib)
    - everything in /sdktools/maya (nothing found)
    - vbsp.vpc (not found sources: disp_ivp.cpp, ivp.cpp, disp_ivp.h, ivp.h; independent project)
    - vaudio_celt.vpc (no lib, no src; independent project)
    - lines 896-902 in client_tf.vpc (group "Useful non-source files")
- Removed ../thirdparty/telemetry/lib/telemetry32.link.lib from tier0.vcxproj
- Modified lines 315-316 in stb_dxt.h
- p4lib copied from /external/vpc/ to root dir
- Changed line /tier2/p4helpers.cpp:94; Add line /public/p4lib/ip4.h:83
- Remove xgraphics.lib, xmaencoder.lib and legacy_stdio_definitions.lib (Xbox-related libs) from Linker->Input in MakeGameData project
- Remove xgraphics.lib, xmaencoder.lib and legacy_stdio_definitions.lib (Xbox-related libs) from Linker->Input in MakeScenesImage project
- Compiled protobuf and placed to /thirdparty/protobuf-2.6.1/bin/win32/2013/staticcrt/release/
- Changed Additional Dep path ..\\..\\thirdparty\\fbx\\FbxSdk\\2015.1\\lib\\vs2012\\x86\\release\\libfbxsdk.lib for project itemtest_com to vs2013
- Copied fbxutils.lib from 2011 to /lib/public
- Made line /vphysics/physics_object.h:237 public
- Added 'false' to /utils/vp4/vp4dialog.cpp:288
- Changed /game/shared/cstrike/achievements_cs.cpp:29 to #include "../../../public/vgui_controls/Controls.h"
- ivp_compactbuilder: Added 8 double()-type castings in /ivp/ivp_compact_builder/qhull_poly2.cxx
- inputsystem: added steam_api.lib to Linder->Additional Dependencies
- hk_math: added some explicit type castings: /ivp/havana/havok/hk_math/gauss_elimination/gauss_elimination.cpp
- gcsdk: disable some warnings in C/C++->Advanced
- engine: changed lines /engine/audio/private/snd_dev_direct.cpp:52-58; copy binkw32.lib to /lib/common from /win32/2015/release (!2015!)
- ivp_physics: disable some warnings in C/C++->Advanced

Not compiled:
- vphysics: no VISUALIZE_COLLISIONS macros
- vaudio_miles: a lot of undefined macroses (grab vaudio_miles.dll from Half-Life 2/bin)
- Studiomdl: studiomdl.cpp undefined vars
- Server (TF) & Client (TF): no compilable deps
- Phonemeextractor_ims: ho file ims_helper.h
- P4lib: no header files; there are outdated incompatible ones from 2007 
- itemtest_lib & itemtest_com: no movieobjects-related and other headers 
- fbxutils & fbx2dmx: no tier0/logging.h
- DX_Proxy (DX9_V00_X360): not needed Xbox-related shit

'''

'''

usage: buildallshaders -pc

----------------------------------------------------------------------------------

set dynamic_shaders=1

----------------------------------------------------------------------------------

set sourcedir="shaders"
set targetdir="..\..\..\game\hl2\shaders"

call buildshaders.bat stdshader_dx9_20b
call buildshaders.bat stdshader_dx9_20b_new -dx9_30
call buildshaders.bat stdshader_dx9_30      -dx9_30 -force30
// call buildshaders.bat stdshader_dx10        -dx10

----------------------------------------------------------------------------------

// usage: buildshaders <shaderProjectName> [-x360]

// USAGE:
// buildshaders <shaderProjectName> [-x360 or -dx10 or -game] [gameDir if -game was specified] [-source sourceDir]"
// gameDir is where gameinfo.txt is (where it will store the compiled shaders)."
// sourceDir is where the source code is (where it will find scripts and compilers)."
// buildshaders myshaders"
// buildshaders myshaders -game c:\steam\steamapps\sourcemods\mymod -source c:\mymod\src"

setlocal
set arg_filename=%1
set shadercompilecommand=shadercompile.exe
set shadercompileworkers=128
set x360_args=
set targetdir=..\..\..\game\hl2\shaders
set SrcDirBase=..\..
set ChangeToDir=../../../game/bin
set shaderDir=shaders
set SDKArgs=
set SHADERINCPATH=vshtmp9/... fxctmp9/...
set DIRECTX_SDK_VER=pc09.00
set DIRECTX_SDK_BIN_DIR=dx9sdk\utilities

if arg_2 == "-dx9_30":
    set DIRECTX_SDK_VER=pc09.30
    set DIRECTX_SDK_BIN_DIR=dx10sdk\utilities\dx9_30
elif arg_2 == "-dx10":
    set DIRECTX_SDK_VER=pc10.00
    set DIRECTX_SDK_BIN_DIR=dx10sdk\utilities\dx10_40
else:
    error

// arg_1 - shaderProjectName (e.g. stdshader_dx9_30)
// arg_2 - -dx9_30 | -dx10 | -game <game_root_dir>
// arg_3 - <game_root_dir> if arg_2 == "-game"
// arg_4 - -source sourceDir
// arg_5 - <sourceDir> if arg_4 == "-source"

set inputbase=%1

if arg_3 == "-force30":
    set DIRECTX_FORCE_MODEL=30

// use the -game parameter to tell us where to put the files
if arg_2 == "-game":
    if not exist %sourcesdk%\bin\shadercompile.exe:
        ERROR: shadercompile.exe doesn't exist in %sourcesdk%\bin

    set ChangeToDir=%sourcesdk%\bin

    if arg_4 != "-source" 
        ERROR: If you specify -game on the command line, you must specify -source.

    set SrcDirBase=%~5
    set targetdir=%~3\shaders
    set SDKArgs=-nompi -game "%~3"

    if not exist "%~3\gameinfo.txt":
        Error: "%~3" is not a valid game directory (The -game directory must have a gameinfo.txt file)


// make sure that target dirs exist
// files will be built in these targets and copied to their final destination
// (shaderDir = materialsystem/stdshaders/shaders)
if not exist %shaderDir% mkdir %shaderDir%
if not exist %shaderDir%\fxc mkdir %shaderDir%\fxc
if not exist %shaderDir%\vsh mkdir %shaderDir%\vsh
if not exist %shaderDir%\psh mkdir %shaderDir%\psh

// Nuke some files that we will add to later.
if exist filelist.txt del /f /q filelist.txt
if exist filestocopy.txt del /f /q filestocopy.txt
if exist filelistgen.txt del /f /q filelistgen.txt
if exist inclist.txt del /f /q inclist.txt
if exist vcslist.txt del /f /q vcslist.txt

// perl "%SrcDirBase%\devtools\bin\p4revertshadertargets.pl" -source "%SrcDirBase%" %inputbase%

// Generate a makefile for the shader project
perl "%SrcDirBase%\devtools\bin\updateshaders.pl" -source "%SrcDirBase%" %inputbase%

// Run the makefile, generating minimal work/build list for fxc files, go ahead and compile vsh and psh files.
// Building inc files, asm vcs files, and VMPI worklist for %inputbase%...
// nmake /S /C -f makefile.%inputbase%

// Copy the inc files to their target
if exist "inclist.txt" (
    // Publishing shader inc files to target...
    perl %SrcDirBase%\devtools\bin\copyshaderincfiles.pl inclist.txt
)

// Add the executables to the worklist.
if /i "%DIRECTX_SDK_VER%" == "pc09.00" (
    rem echo "Copy extra files for dx 9 std
)
if /i "%DIRECTX_SDK_VER%" == "pc09.30" (
    echo %SrcDirBase%\devtools\bin\d3dx9_33.dll >> filestocopy.txt
)
if /i "%DIRECTX_SDK_VER%" == "pc10.00" (
    echo %SrcDirBase%\devtools\bin\d3dx10_33.dll >> filestocopy.txt
)

echo %SrcDirBase%\%DIRECTX_SDK_BIN_DIR%\dx_proxy.dll >> filestocopy.txt
echo %SrcDirBase%\..\game\bin\shadercompile.exe >> filestocopy.txt
echo %SrcDirBase%\..\game\bin\shadercompile_dll.dll >> filestocopy.txt
echo %SrcDirBase%\..\game\bin\vstdlib.dll >> filestocopy.txt
echo %SrcDirBase%\..\game\bin\tier0.dll >> filestocopy.txt

// Cull duplicate entries in work/build list
if exist filestocopy.txt type filestocopy.txt | perl "%SrcDirBase%\devtools\bin\uniqifylist.pl" > uniquefilestocopy.txt
if exist filelistgen.txt if not "%dynamic_shaders%" == "1" (
    echo Generating action list...
    copy filelistgen.txt filelist.txt >nul
    rem %SrcDirBase%\devtools\bin\fxccombogen.exe <filelistgen.txt 1>nul 2>filelist.txt
)

// Execute distributed process on work/build list
set shader_path_cd=%cd%
if exist "filelist.txt" if exist "uniquefilestocopy.txt" if not "%dynamic_shaders%" == "1" (
    echo Running distributed shader compilation...
    cd %ChangeToDir%
    %shadercompilecommand% -mpi_workercount %shadercompileworkers% -allowdebug -shaderpath "%shader_path_cd:/=\%" %x360_args% %SDKArgs%
    cd %shader_path_cd%
)


// PC and 360 Shader copy
// Publish the generated files to the output dir using ROBOCOPY (smart copy) or XCOPY
// This batch file may have been invoked standalone or slaved (master does final smart mirror copy)
if not "%dynamic_shaders%" == "1" (
    if exist makefile.%inputbase%.copy echo Publishing shaders to target...
    if exist makefile.%inputbase%.copy perl %SrcDirBase%\devtools\bin\copyshaders.pl makefile.%inputbase%.copy %x360_args%
)


'''