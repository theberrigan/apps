import re
import sys
import math

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.maths import *
from bfw.media.image.raw import RawImage, PILImage
from bfw.media.image.dxt1 import DXT1
from bfw.native.limits import MAX_I16, MAX_U16
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Games\Call Of Duty 2'
RAW_DIR  = joinPath(GAME_DIR, 'raw')

SCRIPT_EXT = '.gsc'
SCRIPT_ENCODING = 'cp1252'



class TokenType (Enum2):
    pass

'''
https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_CoD_Script_Handbook
https://steamcommunity.com/sharedfiles/filedetails/?id=321216220

-.0
-1. - ???

-[\d.]

------------------------------

// comment
/* multiline comment */
/# code for developer mode only #/
"string"  // note \"
(
)
[[  // [[self.exception_corner_normal]]();
[
]]
]
{
}
.
,
;
::   // charactes\soldier::precace() // thread animscripts\b30cal\common::main(::DoShoot, ::DoRecover, ::DoAim, turret); (::DoShoot == this.DoShoot)
:    // case: default:
*=
*
%<directive>  // %stand_alert_1 - string from animtrees/<name>.atr
%    // mod?
#<directive> (from line start: include, using_animtree)
#/
//
/*
/#
/=
/
--
-=
-
++
+=
+
==
=
!=
!
<=
<
>=
>
&&
&    // bitwise  // &"PLATFORM_USEAION30CAL"
||
\\   // charactes\soldier::precace()

------------------------------

if
else
while
for
break
continue
return
switch
case

undefined
false
true

------------------------------

https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_CoD_Script_Handbook#Keywords

wait     = the time to wait in seconds
self     = an alias to the entity that called the script
level    = an alias to the level (the main script)
waittill = wait until another script notify’s a keyword
notify   = used to trigger waittill
endon    = used to kill a function on a notify
delete   = delete an entity
destroy  = used to destroy structs & hud elements

------------------------------
normal script cannot reference a function in a /# ... #/ comment
return value of developer command can not be accessed if not in a /# ... #/ comment
++ must be applied to an int (applied to %s)
-- must be applied to an int (applied to %s)
first parameter of waittill must evaluate to a string
first parameter of notify must evaluate to a string
first parameter of endon must evaluate to a string
precacheModel must be called before any wait statements in the level script\n
precacheShellShock must be called before any wait statements in the level script\n
precacheItem must be called before any wait statements in the level script\n
precacheShader must be called before any wait statements in the gametype or level script\n
precacheString must be called before any wait statements in the gametype or level script\n
precacheMenu must be called before any wait statements in the level script\n
precacheVehicle must be called before any wait statements in the level script\n
setshadowhint argument must be \""normal\"", \""never\"", \""high_priority\"", \""low_priority\"", \""always\"", or \""receiver\"".

------------------------------
'
'''


class TokenStorage:
    def __init__ (self):
        self.index  = 0
        self.tokens = {}

    def push (self, token):
        self.tokens[self.index] = token
        self.index += 1

    def asList (self):
        tokens = list(self.tokens.items())

        tokens.sort(key=lambda p: p[0])

        return [ p[1] for p in tokens ]


class GSC:
    def __init__ (self):
        self.filePath = None
        self.source   = None
        self.cursor   = None
        self.size     = None
        self.line     = None
        self.column   = None
        self.tokens   = None

    @classmethod
    def parseFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding=SCRIPT_ENCODING)

        return cls().parse(text, filePath)

    @classmethod
    def parseText (cls, text, filePath=None):
        return cls().parse(text, filePath)

    def parse (self, text, filePath):
        self.filePath = filePath
        self.source   = text
        self.cursor   = 0
        self.size     = len(text)
        self.line     = 1
        self.column   = 1
        self.tokens   = TokenStorage()

        # ----------------------------

        while not self.isEnd():
            pass
            # kind
            # source
            # cursorStart
            # cursorEnd
            # startLine
            # startColumn
            # endLine
            # endColumn

        print(text[:100].replace('\n', ' '))

        # ----------------------------

        return self.tokens.asList()

    def addToken (self, token):
        self.tokens.push(token)

    def isEnd (self):
        assert self.cursor <= self.size, (self.cursor, self.size)
        return self.cursor >= self.size


def upperFirstLetter (name):
    if not name:
        return ''

    return name[0].upper() + name[1:]

def dashToCamelCase (name):
    name = name.strip('_')

    if '_' not in name:
        return upperFirstLetter(name)

    name = re.split(r'_+', name)
    name = [ upperFirstLetter(w) for w in name ]

    return ''.join(name)

def createClassNameFromPath (relPath):
    className = dropExt(relPath)
    className = re.split(r'[\\/]+', className)
    className = [ dashToCamelCase(name) for name in className ]
    className = '_'.join(className)

    return className

def parseScripts ():
    for filePath in iterFiles(RAW_DIR, includeExts=[ SCRIPT_EXT ]):
        print(filePath)

        className = createClassNameFromPath(getRelPath(filePath, RAW_DIR))

        fileName = getFileName(filePath)

        # assert fileName == fileName.lower(), fileName

        print(f'export default class { className } {{')

        # script = GSC.parseFile(filePath)

        print(' ')

    # print(toJson(dict([ i for i in _c.items() if len(i[1]) > 1 ])))

    # {
    #     "CProne": [
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\prone.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\b30cal\\prone.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\mg42\\prone.gsc"
    #     ],
    #     "CScripted": [
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\scripted.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\maps\\_scripted.gsc"
    #     ],
    #     "CShared": [
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\shared.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\traverse\\shared.gsc"
    #     ],
    #     "CUtility": [
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\utility.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\maps\\_utility.gsc"
    #     ],
    #     "CCommon": [
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\b30cal\\common.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\mg42\\common.gsc"
    #     ],
    #     "CStand": [
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\b30cal\\stand.gsc",
    #         "G:\\Games\\Call Of Duty 2\\raw\\animscripts\\mg42\\stand.gsc"
    #     ]
    # }


def main ():
    parseScripts()


if __name__ == '__main__':
    main()
