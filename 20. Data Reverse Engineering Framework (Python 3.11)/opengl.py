from typing import Union, List, Tuple, Type, Callable, Any
from ctypes import (
    CDLL,
    cast,
    Array as CArray,
    byref as byRef,
    sizeof as cSizeOf, 
    c_bool as cBool,
    c_char_p as cCP,
    c_float as cF32,
    c_double as cF64,
    c_byte as cI8,
    c_ubyte as cU8,
    c_short as cI16,
    c_ushort as cU16,
    c_int as cI32,
    c_uint as cU32,
    c_longlong as cI64,
    c_ulonglong as cU64,
    c_void_p as cVP,
    POINTER as PTR,
    CFUNCTYPE
)

from time import sleep



def getTypeName (entity):
    return type(entity).__name__

BufferType = CArray[cU8]

def createBuffer (
    size : Union[int, None] = None,
    data : Union[bytes, bytearray, None] = None
) -> BufferType:
    if isinstance(data, bytes):
        data = bytearray(data)

    if data is not None and not isinstance(data, bytearray):
        raise TypeError(f'Specified data must be bytes or bytearray, but { getTypeName(data) } given')

    if size is not None and not isinstance(size, int):
        raise TypeError(f'Specified size must be int, but { getTypeName(size) } given')

    if size is not None and size < 0:
        raise TypeError(f'Specified size must be >= 0, but { size } given')

    if size is None and data is None:
        raise TypeError('Neither data nor buffer size specified')

    dataSize = len(data) if data is not None else 0

    if size is not None and data is not None and size < dataSize:
        raise TypeError(f'Specified buffer size ({ size }) less than data size ({ dataSize })')

    bufferSize = size if size is not None else dataSize
    bufferType = cU8 * bufferSize

    if dataSize > 0:
        return bufferType.from_buffer(data)

    return bufferType()


GLFW_VERSION_MAJOR               = 3
GLFW_VERSION_MINOR               = 3
GLFW_VERSION_REVISION            = 8
GLFW_TRUE                        = 1
GLFW_FALSE                       = 0
GLFW_RELEASE                     = 0
GLFW_PRESS                       = 1
GLFW_REPEAT                      = 2
GLFW_HAT_CENTERED                = 0
GLFW_HAT_UP                      = 1
GLFW_HAT_RIGHT                   = 2
GLFW_HAT_DOWN                    = 4
GLFW_HAT_LEFT                    = 8
GLFW_HAT_RIGHT_UP                = (GLFW_HAT_RIGHT | GLFW_HAT_UP)
GLFW_HAT_RIGHT_DOWN              = (GLFW_HAT_RIGHT | GLFW_HAT_DOWN)
GLFW_HAT_LEFT_UP                 = (GLFW_HAT_LEFT  | GLFW_HAT_UP)
GLFW_HAT_LEFT_DOWN               = (GLFW_HAT_LEFT  | GLFW_HAT_DOWN)
GLFW_KEY_UNKNOWN                 = 1
GLFW_KEY_SPACE                   = 32
GLFW_KEY_APOSTROPHE              = 39
GLFW_KEY_COMMA                   = 44
GLFW_KEY_MINUS                   = 45
GLFW_KEY_PERIOD                  = 46
GLFW_KEY_SLASH                   = 47
GLFW_KEY_0                       = 48
GLFW_KEY_1                       = 49
GLFW_KEY_2                       = 50
GLFW_KEY_3                       = 51
GLFW_KEY_4                       = 52
GLFW_KEY_5                       = 53
GLFW_KEY_6                       = 54
GLFW_KEY_7                       = 55
GLFW_KEY_8                       = 56
GLFW_KEY_9                       = 57
GLFW_KEY_SEMICOLON               = 59
GLFW_KEY_EQUAL                   = 61
GLFW_KEY_A                       = 65
GLFW_KEY_B                       = 66
GLFW_KEY_C                       = 67
GLFW_KEY_D                       = 68
GLFW_KEY_E                       = 69
GLFW_KEY_F                       = 70
GLFW_KEY_G                       = 71
GLFW_KEY_H                       = 72
GLFW_KEY_I                       = 73
GLFW_KEY_J                       = 74
GLFW_KEY_K                       = 75
GLFW_KEY_L                       = 76
GLFW_KEY_M                       = 77
GLFW_KEY_N                       = 78
GLFW_KEY_O                       = 79
GLFW_KEY_P                       = 80
GLFW_KEY_Q                       = 81
GLFW_KEY_R                       = 82
GLFW_KEY_S                       = 83
GLFW_KEY_T                       = 84
GLFW_KEY_U                       = 85
GLFW_KEY_V                       = 86
GLFW_KEY_W                       = 87
GLFW_KEY_X                       = 88
GLFW_KEY_Y                       = 89
GLFW_KEY_Z                       = 90
GLFW_KEY_LEFT_BRACKET            = 91
GLFW_KEY_BACKSLASH               = 92
GLFW_KEY_RIGHT_BRACKET           = 93
GLFW_KEY_GRAVE_ACCENT            = 96
GLFW_KEY_WORLD_1                 = 161
GLFW_KEY_WORLD_2                 = 162
GLFW_KEY_ESCAPE                  = 256
GLFW_KEY_ENTER                   = 257
GLFW_KEY_TAB                     = 258
GLFW_KEY_BACKSPACE               = 259
GLFW_KEY_INSERT                  = 260
GLFW_KEY_DELETE                  = 261
GLFW_KEY_RIGHT                   = 262
GLFW_KEY_LEFT                    = 263
GLFW_KEY_DOWN                    = 264
GLFW_KEY_UP                      = 265
GLFW_KEY_PAGE_UP                 = 266
GLFW_KEY_PAGE_DOWN               = 267
GLFW_KEY_HOME                    = 268
GLFW_KEY_END                     = 269
GLFW_KEY_CAPS_LOCK               = 280
GLFW_KEY_SCROLL_LOCK             = 281
GLFW_KEY_NUM_LOCK                = 282
GLFW_KEY_PRINT_SCREEN            = 283
GLFW_KEY_PAUSE                   = 284
GLFW_KEY_F1                      = 290
GLFW_KEY_F2                      = 291
GLFW_KEY_F3                      = 292
GLFW_KEY_F4                      = 293
GLFW_KEY_F5                      = 294
GLFW_KEY_F6                      = 295
GLFW_KEY_F7                      = 296
GLFW_KEY_F8                      = 297
GLFW_KEY_F9                      = 298
GLFW_KEY_F10                     = 299
GLFW_KEY_F11                     = 300
GLFW_KEY_F12                     = 301
GLFW_KEY_F13                     = 302
GLFW_KEY_F14                     = 303
GLFW_KEY_F15                     = 304
GLFW_KEY_F16                     = 305
GLFW_KEY_F17                     = 306
GLFW_KEY_F18                     = 307
GLFW_KEY_F19                     = 308
GLFW_KEY_F20                     = 309
GLFW_KEY_F21                     = 310
GLFW_KEY_F22                     = 311
GLFW_KEY_F23                     = 312
GLFW_KEY_F24                     = 313
GLFW_KEY_F25                     = 314
GLFW_KEY_KP_0                    = 320
GLFW_KEY_KP_1                    = 321
GLFW_KEY_KP_2                    = 322
GLFW_KEY_KP_3                    = 323
GLFW_KEY_KP_4                    = 324
GLFW_KEY_KP_5                    = 325
GLFW_KEY_KP_6                    = 326
GLFW_KEY_KP_7                    = 327
GLFW_KEY_KP_8                    = 328
GLFW_KEY_KP_9                    = 329
GLFW_KEY_KP_DECIMAL              = 330
GLFW_KEY_KP_DIVIDE               = 331
GLFW_KEY_KP_MULTIPLY             = 332
GLFW_KEY_KP_SUBTRACT             = 333
GLFW_KEY_KP_ADD                  = 334
GLFW_KEY_KP_ENTER                = 335
GLFW_KEY_KP_EQUAL                = 336
GLFW_KEY_LEFT_SHIFT              = 340
GLFW_KEY_LEFT_CONTROL            = 341
GLFW_KEY_LEFT_ALT                = 342
GLFW_KEY_LEFT_SUPER              = 343
GLFW_KEY_RIGHT_SHIFT             = 344
GLFW_KEY_RIGHT_CONTROL           = 345
GLFW_KEY_RIGHT_ALT               = 346
GLFW_KEY_RIGHT_SUPER             = 347
GLFW_KEY_MENU                    = 348
GLFW_KEY_LAST                    = GLFW_KEY_MENU
GLFW_MOD_SHIFT                   = 0x0001
GLFW_MOD_CONTROL                 = 0x0002
GLFW_MOD_ALT                     = 0x0004
GLFW_MOD_SUPER                   = 0x0008
GLFW_MOD_CAPS_LOCK               = 0x0010
GLFW_MOD_NUM_LOCK                = 0x0020
GLFW_MOUSE_BUTTON_1              = 0
GLFW_MOUSE_BUTTON_2              = 1
GLFW_MOUSE_BUTTON_3              = 2
GLFW_MOUSE_BUTTON_4              = 3
GLFW_MOUSE_BUTTON_5              = 4
GLFW_MOUSE_BUTTON_6              = 5
GLFW_MOUSE_BUTTON_7              = 6
GLFW_MOUSE_BUTTON_8              = 7
GLFW_MOUSE_BUTTON_LAST           = GLFW_MOUSE_BUTTON_8
GLFW_MOUSE_BUTTON_LEFT           = GLFW_MOUSE_BUTTON_1
GLFW_MOUSE_BUTTON_RIGHT          = GLFW_MOUSE_BUTTON_2
GLFW_MOUSE_BUTTON_MIDDLE         = GLFW_MOUSE_BUTTON_3
GLFW_JOYSTICK_1                  = 0
GLFW_JOYSTICK_2                  = 1
GLFW_JOYSTICK_3                  = 2
GLFW_JOYSTICK_4                  = 3
GLFW_JOYSTICK_5                  = 4
GLFW_JOYSTICK_6                  = 5
GLFW_JOYSTICK_7                  = 6
GLFW_JOYSTICK_8                  = 7
GLFW_JOYSTICK_9                  = 8
GLFW_JOYSTICK_10                 = 9
GLFW_JOYSTICK_11                 = 10
GLFW_JOYSTICK_12                 = 11
GLFW_JOYSTICK_13                 = 12
GLFW_JOYSTICK_14                 = 13
GLFW_JOYSTICK_15                 = 14
GLFW_JOYSTICK_16                 = 15
GLFW_JOYSTICK_LAST               = GLFW_JOYSTICK_16
GLFW_GAMEPAD_BUTTON_A            = 0
GLFW_GAMEPAD_BUTTON_B            = 1
GLFW_GAMEPAD_BUTTON_X            = 2
GLFW_GAMEPAD_BUTTON_Y            = 3
GLFW_GAMEPAD_BUTTON_LEFT_BUMPER  = 4
GLFW_GAMEPAD_BUTTON_RIGHT_BUMPER = 5
GLFW_GAMEPAD_BUTTON_BACK         = 6
GLFW_GAMEPAD_BUTTON_START        = 7
GLFW_GAMEPAD_BUTTON_GUIDE        = 8
GLFW_GAMEPAD_BUTTON_LEFT_THUMB   = 9
GLFW_GAMEPAD_BUTTON_RIGHT_THUMB  = 10
GLFW_GAMEPAD_BUTTON_DPAD_UP      = 11
GLFW_GAMEPAD_BUTTON_DPAD_RIGHT   = 12
GLFW_GAMEPAD_BUTTON_DPAD_DOWN    = 13
GLFW_GAMEPAD_BUTTON_DPAD_LEFT    = 14
GLFW_GAMEPAD_BUTTON_LAST         = GLFW_GAMEPAD_BUTTON_DPAD_LEFT
GLFW_GAMEPAD_BUTTON_CROSS        = GLFW_GAMEPAD_BUTTON_A
GLFW_GAMEPAD_BUTTON_CIRCLE       = GLFW_GAMEPAD_BUTTON_B
GLFW_GAMEPAD_BUTTON_SQUARE       = GLFW_GAMEPAD_BUTTON_X
GLFW_GAMEPAD_BUTTON_TRIANGLE     = GLFW_GAMEPAD_BUTTON_Y
GLFW_GAMEPAD_AXIS_LEFT_X         = 0
GLFW_GAMEPAD_AXIS_LEFT_Y         = 1
GLFW_GAMEPAD_AXIS_RIGHT_X        = 2
GLFW_GAMEPAD_AXIS_RIGHT_Y        = 3
GLFW_GAMEPAD_AXIS_LEFT_TRIGGER   = 4
GLFW_GAMEPAD_AXIS_RIGHT_TRIGGER  = 5
GLFW_GAMEPAD_AXIS_LAST           = GLFW_GAMEPAD_AXIS_RIGHT_TRIGGER
GLFW_NO_ERROR                    = 0
GLFW_NOT_INITIALIZED             = 0x00010001
GLFW_NO_CURRENT_CONTEXT          = 0x00010002
GLFW_INVALID_ENUM                = 0x00010003
GLFW_INVALID_VALUE               = 0x00010004
GLFW_OUT_OF_MEMORY               = 0x00010005
GLFW_API_UNAVAILABLE             = 0x00010006
GLFW_VERSION_UNAVAILABLE         = 0x00010007
GLFW_PLATFORM_ERROR              = 0x00010008
GLFW_FORMAT_UNAVAILABLE          = 0x00010009
GLFW_NO_WINDOW_CONTEXT           = 0x0001000A
GLFW_FOCUSED                     = 0x00020001
GLFW_ICONIFIED                   = 0x00020002
GLFW_RESIZABLE                   = 0x00020003
GLFW_VISIBLE                     = 0x00020004
GLFW_DECORATED                   = 0x00020005
GLFW_AUTO_ICONIFY                = 0x00020006
GLFW_FLOATING                    = 0x00020007
GLFW_MAXIMIZED                   = 0x00020008
GLFW_CENTER_CURSOR               = 0x00020009
GLFW_TRANSPARENT_FRAMEBUFFER     = 0x0002000A
GLFW_HOVERED                     = 0x0002000B
GLFW_FOCUS_ON_SHOW               = 0x0002000C
GLFW_RED_BITS                    = 0x00021001
GLFW_GREEN_BITS                  = 0x00021002
GLFW_BLUE_BITS                   = 0x00021003
GLFW_ALPHA_BITS                  = 0x00021004
GLFW_DEPTH_BITS                  = 0x00021005
GLFW_STENCIL_BITS                = 0x00021006
GLFW_ACCUM_RED_BITS              = 0x00021007
GLFW_ACCUM_GREEN_BITS            = 0x00021008
GLFW_ACCUM_BLUE_BITS             = 0x00021009
GLFW_ACCUM_ALPHA_BITS            = 0x0002100A
GLFW_AUX_BUFFERS                 = 0x0002100B
GLFW_STEREO                      = 0x0002100C
GLFW_SAMPLES                     = 0x0002100D
GLFW_SRGB_CAPABLE                = 0x0002100E
GLFW_REFRESH_RATE                = 0x0002100F
GLFW_DOUBLEBUFFER                = 0x00021010
GLFW_CLIENT_API                  = 0x00022001
GLFW_CONTEXT_VERSION_MAJOR       = 0x00022002
GLFW_CONTEXT_VERSION_MINOR       = 0x00022003
GLFW_CONTEXT_REVISION            = 0x00022004
GLFW_CONTEXT_ROBUSTNESS          = 0x00022005
GLFW_OPENGL_FORWARD_COMPAT       = 0x00022006
GLFW_OPENGL_DEBUG_CONTEXT        = 0x00022007
GLFW_OPENGL_PROFILE              = 0x00022008
GLFW_CONTEXT_RELEASE_BEHAVIOR    = 0x00022009
GLFW_CONTEXT_NO_ERROR            = 0x0002200A
GLFW_CONTEXT_CREATION_API        = 0x0002200B
GLFW_SCALE_TO_MONITOR            = 0x0002200C
GLFW_COCOA_RETINA_FRAMEBUFFER    = 0x00023001
GLFW_COCOA_FRAME_NAME            = 0x00023002
GLFW_COCOA_GRAPHICS_SWITCHING    = 0x00023003
GLFW_X11_CLASS_NAME              = 0x00024001
GLFW_X11_INSTANCE_NAME           = 0x00024002
GLFW_NO_API                      = 0
GLFW_OPENGL_API                  = 0x00030001
GLFW_OPENGL_ES_API               = 0x00030002
GLFW_NO_ROBUSTNESS               = 0
GLFW_NO_RESET_NOTIFICATION       = 0x00031001
GLFW_LOSE_CONTEXT_ON_RESET       = 0x00031002
GLFW_OPENGL_ANY_PROFILE          = 0
GLFW_OPENGL_CORE_PROFILE         = 0x00032001
GLFW_OPENGL_COMPAT_PROFILE       = 0x00032002
GLFW_CURSOR                      = 0x00033001
GLFW_STICKY_KEYS                 = 0x00033002
GLFW_STICKY_MOUSE_BUTTONS        = 0x00033003
GLFW_LOCK_KEY_MODS               = 0x00033004
GLFW_RAW_MOUSE_MOTION            = 0x00033005
GLFW_CURSOR_NORMAL               = 0x00034001
GLFW_CURSOR_HIDDEN               = 0x00034002
GLFW_CURSOR_DISABLED             = 0x00034003
GLFW_ANY_RELEASE_BEHAVIOR        = 0
GLFW_RELEASE_BEHAVIOR_FLUSH      = 0x00035001
GLFW_RELEASE_BEHAVIOR_NONE       = 0x00035002
GLFW_NATIVE_CONTEXT_API          = 0x00036001
GLFW_EGL_CONTEXT_API             = 0x00036002
GLFW_OSMESA_CONTEXT_API          = 0x00036003
GLFW_ARROW_CURSOR                = 0x00036001
GLFW_IBEAM_CURSOR                = 0x00036002
GLFW_CROSSHAIR_CURSOR            = 0x00036003
GLFW_HAND_CURSOR                 = 0x00036004
GLFW_HRESIZE_CURSOR              = 0x00036005
GLFW_VRESIZE_CURSOR              = 0x00036006
GLFW_CONNECTED                   = 0x00040001
GLFW_DISCONNECTED                = 0x00040002
GLFW_JOYSTICK_HAT_BUTTONS        = 0x00050001
GLFW_COCOA_CHDIR_RESOURCES       = 0x00051001
GLFW_COCOA_MENUBAR               = 0x00051002
GLFW_DONT_CARE                   = 1

GLEW_OK = 0

NULLPTR = 0


def drawTriangle ():
    gl   = CDLL('opengl32.dll')
    glew = CDLL('C:/Projects/_DLL/glew32.dll')
    glfw = CDLL('C:/Projects/_DLL/glfw3.dll')

    # --------------------------------------

    # int glfwInit(void);
    glfw.glfwInit.restype = cI32
    glfw.glfwInit.argtypes = []

    # void glfwTerminate(void);
    glfw.glfwTerminate.restype = None
    glfw.glfwTerminate.argtypes = []

    # void glfwWindowHint(int hint, int value);
    glfw.glfwWindowHint.restype = None
    glfw.glfwWindowHint.argtypes = [
        cI32,
        cI32,
    ]

    # GLFWwindow* glfwCreateWindow(int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share);
    glfw.glfwCreateWindow.restype = cVP
    glfw.glfwCreateWindow.argtypes = [
        cI32,
        cI32,
        cCP,
        cVP,
        cVP
    ]

    # void glfwMakeContextCurrent(GLFWwindow* window);
    glfw.glfwMakeContextCurrent.restype = None
    glfw.glfwMakeContextCurrent.argtypes = [
        cVP
    ]

    # void glfwDestroyWindow(GLFWwindow* window);
    glfw.glfwDestroyWindow.restype = None
    glfw.glfwDestroyWindow.argtypes = [
        cVP
    ]

    # GLEWAPI GLenum GLEWAPIENTRY glewInit (void);
    glew.glewInit.restype = cU32
    glew.glewInit.argtypes = []

    # void glfwGetFramebufferSize(GLFWwindow* window, int* width, int* height);
    glfw.glfwGetFramebufferSize.restype = None
    glfw.glfwGetFramebufferSize.argtypes = [
        cVP,
        cVP,
        cVP
    ]

    # void GLAPIENTRY glViewport (GLint x, GLint y, GLsizei width, GLsizei height);
    gl.glViewport.restype = None
    gl.glViewport.argtypes = [
        cI32,
        cI32,
        cI32,
        cI32
    ]

    # typedef void (* GLFWframebuffersizefun)(GLFWwindow* window, int width, int height);
    # GLFWframebuffersizefun glfwSetFramebufferSizeCallback(GLFWwindow* window, GLFWframebuffersizefun callback);
    GLFWframebuffersizefun = CFUNCTYPE(None, cVP, cI32, cI32)
    glfw.glfwSetFramebufferSizeCallback.restype = GLFWframebuffersizefun
    glfw.glfwSetFramebufferSizeCallback.argtypes = [
        cVP,
        GLFWframebuffersizefun
    ]

    # int glfwWindowShouldClose(GLFWwindow* window);
    glfw.glfwWindowShouldClose.restype = cI32
    glfw.glfwWindowShouldClose.argtypes = [
        cVP
    ]

    # void glfwSwapBuffers(GLFWwindow* window);
    glfw.glfwSwapBuffers.restype = None
    glfw.glfwSwapBuffers.argtypes = [
        cVP
    ]

    # void glfwPollEvents(void);
    glfw.glfwPollEvents.restype = None
    glfw.glfwPollEvents.argtypes = []

    # --------------------------------------

    if not glfw.glfwInit():
        print('Failed to init GLFW')
        return

    glfw.glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4)
    glfw.glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5)
    glfw.glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    pTitle = cCP('LearnOpenGL'.encode('ascii'))

    pWindow = glfw.glfwCreateWindow(800, 600, pTitle, 0, 0)

    if pWindow == NULLPTR:
        glfw.glfwTerminate()
        print('Failed to create window')
        return

    glfw.glfwMakeContextCurrent(pWindow)

    if glew.glewInit() != GLEW_OK:
        glfw.glfwDestroyWindow(pWindow)
        glfw.glfwTerminate()
        print('Failed to init GLEW')
        return

    bufferWidth = cI32(0)
    bufferHeight = cI32(0)

    glfw.glfwGetFramebufferSize(pWindow, byRef(bufferWidth), byRef(bufferHeight))

    bufferWidth = bufferWidth.value
    bufferHeight = bufferHeight.value

    assert bufferWidth == 800 and bufferHeight == 600

    print(f'Framebuffer size: { bufferWidth }x{ bufferHeight }')

    gl.glViewport(cI32(0), cI32(0), cI32(bufferWidth), cI32(bufferHeight))

    fn = GLFWframebuffersizefun(onWindowResize)
    r = glfw.glfwSetFramebufferSizeCallback(pWindow, fn)

    while not glfw.glfwWindowShouldClose(pWindow):
        glfw.glfwSwapBuffers(pWindow)
        glfw.glfwPollEvents()

    # sleep(1)
    glfw.glfwTerminate()

def onWindowResize (a, b, c):
    print('Resized:', a, b, c)


if __name__ == '__main__':
    drawTriangle()
    # b = createBuffer(size=5)
    # print(b)
    # b = createBuffer(size=1)
    # print(b)