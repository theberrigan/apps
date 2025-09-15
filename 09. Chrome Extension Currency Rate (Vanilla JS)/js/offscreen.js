chrome.runtime.onMessage.addListener(({ target, action, options }) => {
    if (target !== 'OFFSCREEN_DOCUMENT') {
        return;
    }

    switch (action) {
        case 'PLAY_NOTIFICATION_SOUND':
            playNotificationSound(options);
            break;
    }
});

const playNotificationSound = ({ soundUrl, volume }) => {
    const audio = new Audio(soundUrl);

    audio.volume = volume;

    audio.play();
};