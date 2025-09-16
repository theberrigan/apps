import {bindMethods, clone} from '../../js/utils';
const config = require('../../config/config.json');

export class VideoGallery {
    public video : any[] = null;

    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        const
            nestEl = document.body.querySelector('.section-main__ratio-nest'),
            selectorEl = document.body.querySelector('.section-main__video-selector');

        this.video = clone(config.video).map(video => {
            video.image = require(`../../images/video_covers/${ video.image }`);

            const videoEl = document.createElement('div');
            videoEl.className = 'section-main__video';

            const coverEl = document.createElement('div');
            coverEl.className = 'section-main__video-cover';
            coverEl.style.backgroundImage = `url('${ video.image }')`;
            videoEl.appendChild(coverEl);
            coverEl.addEventListener('click', () => this.playVideo(video));

            const dotEl = document.createElement('button');
            dotEl.className = 'section-main__video-dot';
            dotEl.type = 'button';
            dotEl.addEventListener('click', () => this.switchVideo(video));

            video.videoEl = videoEl;
            video.dotEl = dotEl;

            nestEl.appendChild(videoEl);
            selectorEl.appendChild(dotEl);

            return video;
        });

        document.body.querySelector('.section-main__button-watch-demo').addEventListener('click', () => {
            const demoVideo = this.video.find(v => v.isDemo);

            if (!demoVideo) {
                return;
            }

            this.switchVideo(demoVideo);
            this.playVideo(demoVideo);
        });

        this.switchVideo(this.video[0]);
    }

    private switchVideo (switchTo : any) : void {
        this.video.forEach(video => {
            if (video.dotEl === switchTo.dotEl) {
                video.videoEl.classList.add('section-main__video_current');
                video.dotEl.classList.add('section-main__video-dot_current');
            } else {
                if (video.playerEl) {
                    video.playerEl.remove();
                    video.playerEl = null;
                    video.videoEl.classList.remove('section-main__video_playing');
                }
                video.videoEl.classList.remove('section-main__video_current');
                video.dotEl.classList.remove('section-main__video-dot_current');
            }
        });
    }

    private playVideo (video : any) : void {
        if (video.playerEl) {
            video.playerEl.remove();
            video.playerEl = null;
        }

        const playerEl = document.createElement('iframe');
        playerEl.className = 'section-main__video-iframe';
        playerEl.allowFullscreen = true;
        playerEl.frameBorder = '0';
        playerEl.setAttribute('allow', 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture');
        playerEl.src = `https://www.youtube.com/embed/${ video.youtubeId }?autoplay=1`;

        video.playerEl = playerEl;

        video.videoEl.appendChild(playerEl);
        video.videoEl.classList.add('section-main__video_playing');
    }
}