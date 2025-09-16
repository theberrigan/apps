import os
import re
import sys
import tempfile
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.types.enums import Enum
from bfw.native.base import BIN_DIR



SEVENZIP_DIR      = joinPath(BIN_DIR, '7zip')
SEVENZIP_7Z_PATH  = joinPath(SEVENZIP_DIR, '7z.exe')
SEVENZIP_7ZG_PATH = joinPath(SEVENZIP_DIR, '7zG.exe')



class SevenZipPathMode (Enum):
    Relative     = 1  # "C:\path\to\file\item.txt" -> "item.txt"
    RootRelative = 2  # "C:\path\to\file\item.txt" -> "path\to\file\item.txt"
    Absolute     = 3  # "C:\path\to\file\item.txt" -> "C:\path\to\file\item.txt"
    Default      = Relative

'''
7z <command> [<switch>...] <base_archive_name> [<arguments>...]

<arguments> ::= <switch> | <wildcard> | <filename> | [@listfile] 
<switch>::= -{switch_name}
'''

class SevenZip:
    @classmethod
    def pack (cls, *,
        includePaths    = None, 
        excludePaths    = None,
        includeListPath = None, 
        excludeListPath = None,
        archivePath     = None,
        hideOutput      = False,
        pathMode        = SevenZipPathMode.Default,
        useConsole      = False,
        exePath         = None,
    ):

        if not isinstance(useConsole, bool):
            raise Exception('Argument "useConsole" expected to be True or False')

        if exePath is None:
            if useConsole:
                exePath = SEVENZIP_7Z_PATH
            else:
                exePath = SEVENZIP_7ZG_PATH
        elif not isinstance(exePath, str):
            raise Exception(f'Argument "exePath" expected to be a str or None, "{ exePath }" given')

        exePath = getAbsPath(exePath)

        if not isFile(exePath):
            raise Exception(f'Executable does not exist: { exePath }')

        # ------------------------

        if not isinstance(archivePath, str):
            raise Exception(f'Argument "archivePath" expected to be a str, "{ archivePath }" given')

        if not archivePath:
            raise Exception(f'Argument "archivePath" expected to be a non-empty str')

        archivePath = getAbsPath(archivePath)

        # ------------------------

        match pathMode:
            case SevenZipPathMode.Relative:
                pathMode = None

            case SevenZipPathMode.RootRelative:
                pathMode = '-spf2'

            case SevenZipPathMode.Absolute:
                pathMode = '-spf'

            case _:
                raise Exception(f'Argument "pathMode" has invalid value "{ pathMode }"')

        # ------------------------

        if includePath is not None and listPath is not None:
            raise Exception(f'Expected only "includePath" or "listPath" argument, not both')

        if excludePath is not None and listPath is not None:
            raise Exception(f'Expected only "excludePath" or "listPath" argument, not both')

        if includePath is not None:
            if isStr(includePath):
                includePath = [ includePath ]
            elif not isList(includePath):
                raise Exception(f'Argument "includePath" expected to be a non-empty string or a list of non-empty strings, "{ getType(includePath) }" given')

            for i, path in enumerate(includePath):
                if not isStr(path):
                    raise Exception(f'Argument "includePath" list item expected to be a string, but item { i } has type { getType(path) }')

                path = path.strip()

                if not path:
                    raise Exception(f'Argument "includePath" list item expected to be a non-empty string, but item { i } is empty string')                

                includePath[i] = path

        includePath = includePath or []

        if excludePath is not None:
            if isStr(excludePath):
                excludePath = [ excludePath ]
            elif not isList(excludePath):
                raise Exception(f'Argument "excludePath" expected to be a non-empty string or a list of non-empty strings, "{ getType(excludePath) }" given')

            for i, path in enumerate(excludePath):
                if not isStr(path):
                    raise Exception(f'Argument "excludePath" list item expected to be a string, but item { i } has type { getType(path) }')

                path = path.strip()

                if not path:
                    raise Exception(f'Argument "excludePath" list item expected to be a non-empty string, but item { i } is empty string')                

                excludePath[i] = path

        excludePath = excludePath or []

        if listPath is not None:
            if not isStr(listPath):
                raise Exception(f'Argument "listPath" expected to be a string, "{ getType(listPath) }" given')

            listPath = listPath.strip()

            if not listPath:
                raise Exception(f'Argument "listPath" expected to be a non-empty string, but empty string given')

            listPath = getAbsPath(listPath)

            if not isFile(listPath):
                raise Exception(f'File list does not exist: { listPath }')

        if not includePath and not listPath:
            raise Exception('Input files are not specified')

        isFileListMode = bool(listPath)

        if isFileListMode:
            tempDir = tempfile.gettempdir()

            tempUUID = createUUID(asHex=True, toUpperCase=True)

            includeFileListPath = joinPath(tempDir, f'bfw_7z_i_{ tempUUID }.txt')
            excludeFileListPath = joinPath(tempDir, f'bfw_7z_e_{ tempUUID }.txt')

            with open(listPath, 'r', encoding='utf-8') as listFile, \
                 open(includeFileListPath, 'w', encoding='utf-8') as inFile, \
                 open(excludeFileListPath, 'w', encoding='utf-8') as exFile:

                i = 0

                while True:
                    line = listFile.readline()

                    i += 1

                    if not line:
                        break

                    line = line.strip()

                    if not line:
                        continue

                    match = re.match(r'^\<([^\>]+)\>(.*)$', line)

                    if match:
                        param = match[1]
                        line  = match[2]

                        if param != 'e':
                            raise Exception(f'Unexpected file parameter "{ param }" on line { i } of file list')

                        exFile.write(f'{ line }\n')
                    else:
                        inFile.write(f'{ line }\n')                    

        else:
            includeFileListPath = None
            excludeFileListPath = None
        
        # ------------------------

        cmd = []

        cmd.append(exePath)
        cmd.append('a')     # command
        cmd.append('-t7z')  # *.7z archive
        cmd.append(archivePath)
        cmd.append('-scsUTF-8')  # filelist file encoding

        if pathMode:
            cmd.append(pathMode)

        if hideOutput:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
            stdin  = subprocess.PIPE
        else:
            stdout = sys.stdout
            stderr = sys.stderr
            stdin  = sys.stdin


        # 7z a -tzip src.zip *.txt -ir!DIR1\*.cpp
        # 7z a -tzip archive.zip @listfile.txt
        # 7z x archive.zip -oc:\Doc

        '''
        cmd.append('-bb3')  # verbosity
        
        cmd.append('-bso1')  # stdout -> stdout
        cmd.append('-bse2')  # stderr -> stderr 
        cmd.append('-bsp1')  # progress -> stdout

        cmd.append('-m0=BCJ2')
        cmd.append('-m1=LZMA2:x=9:d=1g')
        # cmd.append('-mx=9')
        cmd.append('-myx=9')
        # cmd.append('-md=1g')
        cmd.append('-ms=on')
        cmd.append('-mmemuse=p80')
        '''

        if isFileListMode:
            assert includeFileListPath, includeFileListPath
            assert excludeFileListPath, excludeFileListPath

            cmd.append(f'-i@{ includeFileListPath }')
            cmd.append(f'-x@{ excludeFileListPath }')

        else:
            for path in includePath:
                cmd.append(f'-i!{ path }')

            for path in excludePath:
                cmd.append(f'-x!{ path }')

        print(cmd); exit()

        # TODO: remove existing archive, add "overwrite" fn arg

        process = subprocess.run(cmd, stdout=stdout, stderr=stderr, stdin=stdin)

        if process.returncode != 0:
            if hideOutput:
                error = (process.stdout + b' ' + process.stderr).decode('utf-8')
            else:
                error = ''

            if error:
                error = f'Failed to pack files: { error }'
            else:                
                error = f'Failed to pack files'

            raise Exception(error)

        # 




def _test_ ():
    pass



__all__ = [
    'SevenZip',
    'SevenZipPathMode'
]



if __name__ == '__main__':
    _test_()
