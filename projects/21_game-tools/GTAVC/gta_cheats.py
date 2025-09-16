from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
from time import sleep

keyboard = KeyboardController()

isCycling = False

def pressKey (key):
    keyboard.press(key)
    keyboard.release(key)

def getVK (key):
    return key.vk if hasattr(key, 'vk') else None

def pressStreak (streak, count=1):
    for i in range(count):
        for key in streak:
            sleep(0.1)
            pressKey(key)

def GTAVCCheats ():
    def onKeyUp (key):
        '''
        global isCycling
        if getVK(key) == 99:        
            isCycling = not isCycling
            print('isCycling', isCycling)
        '''

        if getVK(key) == 81 or getVK(key) == 97 or key == Key.alt_l:
            pressStreak('aspirine')
            pressStreak('preciousprotection')        
        elif getVK(key) == 98:
            pressStreak('nuttertools', 20)

    with KeyboardListener(on_release=onKeyUp) as kbListener:
        kbListener.join()

def GTASACheats ():
    def onKeyUp (key):
        if getVK(key) == 81 or key == Key.alt_l:
            pressStreak('hesoyam')

    with KeyboardListener(on_release=onKeyUp) as kbListener:
        kbListener.join()

GTASACheats()



'''
with KeyboardListener(on_release=onKeyUp) as kbListener:
    kbListener.join()

while True:
    if isCycling:
        keyboard.press(Key.shift_l)
        sleep(0.075)
        keyboard.release(Key.shift_l)
        sleep(0.1)
'''

'''
KB_KEY_E = 69

class SIlentHill2:
    def onKeyDown (self, key):
        vkKeyCode = getVK(key)

        if vkKeyCode == KB_KEY_E:
            print('kbDown', vkKeyCode)

    def onKeyUp (self, key):
        vkKeyCode = getVK(key)

        if vkKeyCode == KB_KEY_E:
            print('kbUp', vkKeyCode)

    def onClick (self, x, y, button, isPressing):
        if button == Button.right:
            if isPressing:
                keyboard.press('e')
            else:
                keyboard.release('e')

        print('mouse', x, y, button, isPressing)

    def listen (self):
        kbListener = KeyboardListener(on_press=self.onKeyDown, on_release=self.onKeyUp)
        kbListener.start()

        with MouseListener(on_click=self.onClick) as mListener:
            mListener.join()


SIlentHill2().listen()
'''