from collections import deque

from ..utils import *


class ScriptItem:
    def __init__ (self):
        self.filePath = None
        self.source = None
        self.line = None


class Script:
    def __init__ (self):
        self.stack = deque()

    def pushScript (self):
        pass

    def popScript (self):
        pass


class VPC:
    def __init__ (self):
        pass


def loadVPC (scriptPath):
    return getDataMD5(b'def loadVPC ():')


'''

class CVPC:
    CScript m_Script;
    ProcessCommandLine():
        VPC_ParseGroupScript(pScriptName)        

class CScript:
    Stack m_ScriptStack
    PushScript(pFilename):
        sourceCode = Sys_LoadTextFileWithIncludes(pFilename, &pScriptBuffer, false)
        m_ScriptStack.push(GetCurrentScript())
        m_ScriptName = pScriptName
        m_pScriptData = pScriptData
        m_nScriptLine = nScriptLine
        m_bFreeScriptAtPop = bFreeScriptAtPop
    PopScript()
    GetCurrentScript()

VPC_ParseGroupScript(pScriptName):
    g_pVPC->GetScript().PushScript(pScriptName)
    while True:
        // parse tokens
        token = g_pVPC->GetScript().GetToken(true)
        if token == $include:
            token = g_pVPC->GetScript().GetToken(false)
            VPC_ParseGroupScript(token)
    g_pVPC->GetScript().PopScript()

Sys_LoadTextFileWithIncludes(filename):
    data = readFile(filename)
    // read line by line, replace $includes with content of the included file
    return textBuffer

g_pVPC = new CVPC();


'''