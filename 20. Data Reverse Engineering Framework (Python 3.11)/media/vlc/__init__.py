import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.utils import *

addEnvPath(r'D:\Apps\vlc-3.0.18')

# pip install python-vlc
import vlc as PyVLC



HTTP_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36'



# https://wiki.videolan.org/VLC_command-line_help/
# https://wiki.videolan.org/Documentation:Streaming_HowTo/Advanced_Streaming_Using_the_Command_Line/
class VLCDownloader:
    def __init__ (self):
        self.isComplete  = False
        self.lastPercent = None
        self.player      = None

    def download (self, sourceUrl, destPath):
        print(f'Downloading...')
        print(f'Source: { sourceUrl }')
        print(f'Output: { destPath }')

        self.isComplete  = False
        self.lastPercent = None

        startTime = getTimestamp()

        vlc = PyVLC.Instance()

        # disable logging
        vlc.log_unset()

        self.player = player = vlc.media_player_new()

        media = vlc.media_new(sourceUrl, f'sout=file/ts:{ destPath }', f"http-user-agent='{ HTTP_USER_AGENT }'")
  
        player.set_media(media)

        eventManager = player.event_manager()
        eventManager.event_attach(PyVLC.EventType.MediaPlayerPositionChanged, self.onPositionChanged)
        # self.eventManager.event_attach(vlc.EventType.MediaPlayerEndReached, self.onEndReached)
        eventManager.event_attach(PyVLC.EventType.MediaPlayerStopped, self.onStopped)

        player.play()

        while not self.isComplete:
            sleep(1)

        player.release()

        self.isComplete  = False
        self.lastPercent = None
        self.player      = None

        timeWasted = formatTimestamp(getTimestamp() - startTime)

        print(f'Complete (time wasted: { timeWasted })')
        print(' ')


    def _onEvent (self, event):
        print('Event', PyVLC.EventType(event.type))

    def onPositionChanged (self, event):
        percent = round(self.player.get_position() * 100)

        if self.lastPercent == None or (percent % 10 == 0 and self.lastPercent != int(percent)):
            self.lastPercent = int(percent)

            completeDuration = formatTimestamp(self.player.get_time())
            totalDuration = formatTimestamp(self.player.get_length())

            print(f'{ percent }% ({ completeDuration } of { totalDuration })')

    def onStopped (self, event):
        self.isComplete = True



__all__ = [
    'VLCDownloader'
]



if __name__ == '__main__':
    pass