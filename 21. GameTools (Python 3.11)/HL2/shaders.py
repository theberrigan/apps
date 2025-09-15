import os, sys, regex, shutil, hashlib, json

from utils import *


CLI_DIR = getDirPath(getAbsPath(__file__))

ROOT_DIR = getAbsPath(r'C:\Projects\_Sources\GameEngines\SourceEngine2013_5')

SRC_DIR  = joinPath(ROOT_DIR, 'Source')
STD_SHADERS_DIR = joinPath(SRC_DIR, 'materialsystem', 'stdshaders')

LAUNCH_DIR     = joinPath(ROOT_DIR, 'Content')
HL2_GAME_DIR   = joinPath(LAUNCH_DIR, 'hl2')
SOURCE_SDK_DIR = joinPath(LAUNCH_DIR, 'bin')
COMPILER_PATH  = joinPath(SOURCE_SDK_DIR, 'shadercompile.exe')

DX9_00_UTILS_DIR  = joinPath(SRC_DIR, 'dx9sdk',  'utilities')
DX9_30_UTILS_DIR  = joinPath(SRC_DIR, 'dx10sdk', 'utilities', 'dx9_30')

NMAKE_PATH = r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\bin\nmake.exe'


def checkVCSUpToDate (sourcePath, vcsPath):
    if not isFile(sourcePath) or not isFile(vcsPath):
        return False

    return getFileCRC32(sourcePath) == getVCSCRC(vcsPath)


def getVCSCRC (vcsPath):
    if getFileSize(vcsPath) < 28:
        return 0

    with open(vcsPath, 'rb') as f:
        version = readStruct('<i', f)

        if version < 4 or version > 6:
            return 0

        f.seek(24)

        return readStruct('<I', f)

# -projectName
# -game -source
# -force30

class ShaderCompiler:
    def __init__ (self):
        self.dynamicOnly        = False
        self.projectName        = None  # ex: stdshader_dx9_20b 
        self.sourceDir          = None  # ex: SourceEngine2013_5/Source
        self.gameDir            = None  # ex: SourceEngine2013_5/Content/hl2
        self.stdShadersDir      = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders
        self.sourceSDKDir       = None  # ex: SourceEngine2013_5/Content/bin
        self.compilerPath       = None  # ex: SourceEngine2013_5/Content/bin/shadercompile.exe
        self.destDir            = None  # ex: SourceEngine2013_5/Content/hl2/shaders
        self.localDestDir       = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/shaders
        self.model              = None  # ex: 'dx9_00' or 'dx9_30'
        self.isForced30         = False
        self.dxSDKVersion       = None  # DIRECTX_SDK_VER
        self.dxSDKBinDir        = None  # DIRECTX_SDK_BIN_DIR; ex: SourceEngine2013_5/Source/dx10sdk/utilities/dx9_30
        self.dxForceModel       = None  # DIRECTX_FORCE_MODEL
        self.fileListPath       = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/filelist.txt
        self.copyListPath       = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/filestocopy.txt
        self.uniqueCopyListPath = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/uniquefilestocopy.txt
        self.fileListGenPath    = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/filelistgen.txt
        self.incListPath        = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/inclist.txt
        self.vcsListPath        = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/vcslist.txt
        self.makeFilePath       = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/makefile.stdshader_dx9_20b
        self.makeFileCopyPath   = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/makefile.stdshader_dx9_20b.copy
        self.projectFilePath    = None  # ex: SourceEngine2013_5/Source/materialsystem/stdshaders/stdshader_dx9_20b.txt

    def compileDynamicShaders (self):
        self.dynamicOnly = True
        self.compileAllShaders()

    def compileAllShaders (self):
        self.compileShaders('stdshader_dx9_20b')
        self.compileShaders('stdshader_dx9_20b_new', model='dx9_30')
        self.compileShaders('stdshader_dx9_30', model='dx9_30', isForced30=True)

    def compileGameShaders (self, projectName, sourceDir=SRC_DIR, gameDir=HL2_GAME_DIR, model='dx9_00', isForced30=False):
        print('Collecting shaders...')

        self.model        = model
        self.isForced30   = isForced30
        self.dxSDKVersion = 'pc09.00'         # DIRECTX_SDK_VER
        self.dxSDKBinDir  = DX9_00_UTILS_DIR  # DIRECTX_SDK_BIN_DIR
        self.dxForceModel = ''                # DIRECTX_FORCE_MODEL

        if self.model == 'dx9_30':
            self.dxSDKVersion = 'pc09.30'
            self.dxSDKBinDir  = DX9_30_UTILS_DIR

        # TODO: remove?
        if self.isForced30:
            self.dxForceModel = '30'

        self.sourceDir     = getAbsPath(sourceDir)
        self.stdShadersDir = getAbsPath(joinPath(self.sourceDir, 'materialsystem', 'stdshaders'))
        self.gameDir       = getAbsPath(gameDir)
        self.sourceSDKDir  = getAbsPath(joinPath(self.gameDir, '..', 'bin'))
        self.compilerPath  = getAbsPath(joinPath(self.sourceSDKDir, 'shadercompile.exe'))

        if not isDir(self.sourceDir):
            raise Exception(f'Source directory does not exist: { self.sourceDir }')

        if not isDir(self.stdShadersDir):
            raise Exception(f'Stdshaders directory does not exist: { self.stdShadersDir }')

        if not isFile(joinPath(self.gameDir, 'gameinfo.txt')):
            raise Exception(f'This is not a game directory: { self.gameDir }')

        if not isFile(self.compilerPath):
            raise Exception(f'Compiler path does not exist: { self.compilerPath }')

        os.chdir(self.stdShadersDir)

        # ! set ChangeToDir=%sourcesdk%\bin
        # i sourceDir == SrcDirBase

        self.destDir      = getAbsPath(joinPath(self.gameDir, 'shaders'))
        self.localDestDir = getAbsPath(joinPath(self.stdShadersDir, 'shaders'))

        # ! sdkArgs = [ '-nompi', '-game', self.gameDir ]

        createDirs(joinPath(self.localDestDir, 'fxc'))
        createDirs(joinPath(self.localDestDir, 'vsh'))
        createDirs(joinPath(self.localDestDir, 'psh'))

        self.fileListPath       = getAbsPath(joinPath(self.stdShadersDir, 'filelist.txt'))
        self.copyListPath       = getAbsPath(joinPath(self.stdShadersDir, 'filestocopy.txt'))
        self.uniqueCopyListPath = getAbsPath(joinPath(self.stdShadersDir, 'uniquefilestocopy.txt'))
        self.fileListGenPath    = getAbsPath(joinPath(self.stdShadersDir, 'filelistgen.txt'))
        self.incListPath        = getAbsPath(joinPath(self.stdShadersDir, 'inclist.txt'))
        self.vcsListPath        = getAbsPath(joinPath(self.stdShadersDir, 'vcslist.txt'))
        self.makeFilePath       = getAbsPath(joinPath(self.stdShadersDir, f'makefile.{ projectName }'))
        self.makeFileCopyPath   = getAbsPath(joinPath(self.stdShadersDir, f'makefile.{ projectName }.copy'))
        self.projectFilePath    = getAbsPath(joinPath(self.stdShadersDir, f'{ projectName }.txt'))

        removeFile(self.fileListPath)
        removeFile(self.copyListPath)
        removeFile(self.uniqueCopyListPath)
        removeFile(self.fileListGenPath)
        removeFile(self.incListPath)
        removeFile(self.vcsListPath)

        if not isFile(self.projectFilePath):
            raise Exception(f'Project file does not exist: { self.projectFilePath }')

        sourcePairs = self.readProjectFile()

        with open(self.makeFilePath, 'w', encoding='utf-8') as makeOut, \
             open(self.makeFileCopyPath, 'w', encoding='utf-8') as copyOut, \
             open(self.incListPath, 'w', encoding='utf-8') as incOut, \
             open(self.vcsListPath, 'w', encoding='utf-8') as vcsOut:

            # --------------------------------------------------------------

            makeOut.write('default: ')

            for shaderType, sourcePath, targetFileName in sourcePairs:
                # $shadertype = shaderType
                # $shaderbase = targetFileName
                # $shadersrc  = sourcePath

                if shaderType in [ 'fxc', 'vsh' ]:
                    incPath = self.getIncTempPath(shaderType, targetFileName)

                    makeOut.write(' ' + incPath)
                    incOut.write(incPath + '\n')

                vcsBaseName = targetFileName + '.vcs'
                vcsDestPath = joinPath(self.destDir, shaderType, vcsBaseName)

                needCompileVCS = not(shaderType == 'fxc' and self.dynamicOnly)

                if needCompileVCS:
                    vcsOut.write(vcsDestPath + '\n')  # DIFF: abs path
                    needCompileVCS = not checkVCSUpToDate(sourcePath, vcsDestPath)

                if needCompileVCS:
                    makeOut.write(' ' + joinPath('shaders', shaderType, vcsBaseName))
                    copyOut.write(f'{ sourcePath }-----{ targetFileName }\n')

            makeOut.write('\n\n')

            # --------------------------------------------------------------

            lastSourcePath = None
            deps = []

            for shaderType, sourcePath, targetFileName in sourcePairs:
                if sourcePath != lastSourcePath:
                    lastSourcePath = sourcePath
                    sourceAbsPath = getAbsPath(joinPath(self.stdShadersDir, sourcePath))
                    deps = self.collectShaderDeps(sourceAbsPath)

                self.asmShader(
                    (shaderType, sourcePath, targetFileName), 
                    (makeOut, copyOut, incOut, vcsOut),
                    deps
                )

        if not getFileSize(self.makeFileCopyPath):
            removeFile(self.makeFileCopyPath)

        print('Running nmake...')

        self.runNmake()

        print('Copying include files...')

        self.copyIncludeFiles()

        with open(self.copyListPath, 'a', encoding='utf-8') as f:
            if self.dxSDKVersion == 'pc09.30':
                f.write(joinPath(self.sourceDir, 'devtools', 'bin', 'd3dx9_33.dll') + '\n')

            f.write(joinPath(self.dxSDKBinDir, 'dx_proxy.dll') + '\n')
            f.write(joinPath(self.sourceSDKDir, 'shadercompile.exe') + '\n')
            f.write(joinPath(self.sourceSDKDir, 'shadercompile_dll.dll') + '\n')
            f.write(joinPath(self.sourceSDKDir, 'vstdlib.dll') + '\n')
            f.write(joinPath(self.sourceSDKDir, 'tier0.dll') + '\n')

        with open(self.copyListPath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        filesToCopy = {}

        for filePath in lines:
            filePath = filePath.strip()  # DIFF: some paths are abs

            filesToCopy[getAbsPath(filePath).lower()] = filePath

        filesToCopy = sorted(filesToCopy.values())

        with open(self.uniqueCopyListPath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(filesToCopy) + '\n')


    def runNmake (self):
        nmakeProc = subprocess.run([ NMAKE_PATH, '/NOLOGO', '/f', self.makeFilePath ], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

        if nmakeProc.returncode != 0:
            raise Exception('Nmake failed')

    def copyIncludeFiles (self):
        with open(self.incListPath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for sourcePath in lines:
            sourcePath = sourcePath.split('//')[0]  # drop comments
            sourcePath = sourcePath.strip()

            if not sourcePath:
                continue

            sourcePath   = joinPath(self.stdShadersDir, sourcePath)
            destDir      = getDirPath(sourcePath)
            destBaseName = getBaseName(sourcePath)

            if destDir.lower().endswith('_tmp'):
                destDir = destDir[:-4]

            destPath = joinPath(destDir, destBaseName)

            if isFile(destPath):
                setReadOnly(destPath, False)
            else:
                createDirs(destDir)

            shutil.copy(sourcePath, destPath)


    def getIncTempPath (self, shaderType, targetFileName):
        return joinPath(f'{ shaderType }tmp9_tmp', f'{ targetFileName }.inc')

    def asmShader (self, shader, outFiles, deps):
        shaderType, sourcePath, targetFileName = shader
        makeOut, copyOut, incOut, vcsOut = outFiles

        incPath = ''

        if shaderType in [ 'fxc', 'vsh' ]:
            incPath = self.getIncTempPath(shaderType, targetFileName)

        vcsBaseName = targetFileName + '.vcs'
        vcsDestPath = joinPath(self.destDir, shaderType, vcsBaseName)

        needCompileVCS = not(shaderType == 'fxc' and self.dynamicOnly)

        if needCompileVCS:
            needCompileVCS = not checkVCSUpToDate(sourcePath, vcsDestPath)

        if needCompileVCS:
            vcsPath  = joinPath('shaders', shaderType, vcsBaseName)
            depPaths = ' '.join(deps)

            include = incPath + (' ' if incPath else '')

            makeOut.write(f'{ include }{ vcsPath }: { sourcePath } { depPaths }\n')

        elif shaderType in [ 'fxc', 'vsh' ]:
            makeOut.write(f'{ incPath }: { sourcePath } { depPaths }\n')

        switches = []

        if not needCompileVCS and shaderType == 'fxc':
            switches.append('-novcs')

        if not (shaderType == 'psh' and not needCompileVCS):
            prepScriptPath = getAbsPath(joinPath(self.sourceDir, 'devtools', 'bin', f'{ shaderType }_prep.pl'))

            assert isFile(prepScriptPath)

            switches = ' '.join(switches)

            makeOut.write(f'\tperl "{ prepScriptPath }" { switches } -source "{ self.sourceDir }" { sourcePath }-----{ targetFileName }\n')

        if needCompileVCS:
            makeOut.write(f'\techo { sourcePath }>> filestocopy.txt\n')

            for dep in deps:
                makeOut.write(f'\techo { dep }>> filestocopy.txt\n')

        makeOut.write('\n')

    def collectShaderDeps (self, sourcePath):
        def walk (sourcePath, deps):
            if not isFile(sourcePath):
                raise Exception(f'Shader source file does not exist: { sourcePath }')

            with open(sourcePath, 'r', encoding='cp1251') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                match = regex.match(r'^#\s*include\s+"([^"]+)"', line)

                if not match:
                    continue

                depAbsPath = getAbsPath(joinPath(self.stdShadersDir, match.group(1)))
                depRelPath = getRelPath(depAbsPath, self.stdShadersDir)

                deps[depAbsPath.lower()] = depRelPath

                walk(depAbsPath, deps)

            return deps

        return sorted(list(walk(sourcePath, {}).values()))

    def readProjectFile (self):
        with open(self.projectFilePath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        sourcePairs = []
        model30repls = [
            (r'_ps2x$',  '_ps30'),
            (r'_ps20b$', '_ps30'),
            (r'_ps20$',  '_ps30'),
            (r'_vs20$',  '_vs30'),
            (r'_vsxx$',  '_vs30'),
        ]

        for sourcePath in lines:
            sourcePath = sourcePath.split('//')[0]  # drop comments
            sourcePath = sourcePath.strip()

            if not sourcePath:
                continue

            # ? sourcePath = getAbsPath(joinPath(stdShadersDir, sourcePath))
            shaderType = getExt(sourcePath, True)

            if shaderType not in [ 'fxc', 'vsh', 'psh' ]:
                continue

            sourceFileName = getFileName(sourcePath)

            if self.isForced30:
                targetFileName = sourceFileName

                for replWhat, replWith in model30repls:
                    targetFileName = regex.sub(replWhat, replWith, targetFileName)

                sourcePairs.append((shaderType, sourcePath, targetFileName))

            elif sourceFileName.lower().endswith('_ps2x'):
                targetFileName = regex.sub(r'_ps2x$', '_ps20', sourceFileName)
                sourcePairs.append((shaderType, sourcePath, targetFileName))

                targetFileName = regex.sub(r'_ps2x$', '_ps20b', sourceFileName)
                sourcePairs.append((shaderType, sourcePath, targetFileName))

            elif sourceFileName.lower().endswith('_vsxx'):
                targetFileName = regex.sub(r'_vsxx$', '_vs11', sourceFileName)
                sourcePairs.append((shaderType, sourcePath, targetFileName))

                targetFileName = regex.sub(r'_vsxx$', '_vs20', sourceFileName)
                sourcePairs.append((shaderType, sourcePath, targetFileName))

            else:
                sourcePairs.append((shaderType, sourcePath, sourceFileName))

        return sourcePairs


if __name__ == '__main__':
    # main()
    ShaderCompiler().compileGameShaders('stdshader_dx9_20b')
