const MarkerState = {
    Default:  1,
    Progress: 2,
    Complete: 3
};

const getMarkerState = (marker) => {
    return marker.state || MarkerState.Default;
};

const isLeftMouseButton = (e, checkModKeys) => {
    return e.button === 0 && (!checkModKeys || !e.altKey && !e.ctrlKey && !e.shiftKey);
};

const isRightMouseButton = (e, checkModKeys) => {
    return e.button === 2 && (!checkModKeys || !e.altKey && !e.ctrlKey && !e.shiftKey);
};

const fetchMapData = async () => {
    const response = await fetch('/map-data', {
        method: 'GET',
    }).then((response) => {
        return response.json();
    }).then((response) => {
        if (response.isOk) {
            return response.data;
        }

        return null;
    }).catch((e) => { 
        console.warn('Failed to fetch map data:', e);

        return null;
    });

    return response;
};

const saveMapData = (() => {
    let timeout = null;

    return async (data) => {
        if (timeout !== null) {
            clearTimeout(timeout);
            timeout = null;
        }

        timeout = setTimeout(async () => {
            timeout = null;

            const response = await fetch('/map-data', {
                method: 'POST',
                body: JSON.stringify(data)
            }).then((response) => {
                return response.json();
            }).catch((e) => { 
                console.warn('Failed to save map data:', e);

                return null;
            });

            if (!response || !response.isOk) {
                alert('Failed to save');
            }
        }, 1500);
    };
})();

const init = async () => {
    const panelEl   = document.body.querySelector('.panel');
    const visBtnEl  = panelEl.querySelector('.panel__button_visibility');
    const mapEl     = document.body.querySelector('.map');
    const mapContEl = mapEl.querySelector('.map__container');
    const markersEl = mapEl.querySelector('.map__markers');

    const zoomStep  = 0.15;
    const minZoom   = 0.1;
    const maxZoom   = 1.2;
    const mapWidth  = mapContEl.clientWidth;
    const mapHeight = mapContEl.clientHeight;

    // mapWidth === mapHeight;
    let mapCurWidth  = mapWidth;
    let mapCurHeight = mapHeight;
    let mapLeft      = 0;
    let mapTop       = 0;
    let isMoving     = false;

    mapContEl.addEventListener('wheel', (e) => {
        if (isMoving) {
            return;
        }

        const delta = e.wheelDeltaY;

        if (delta === 0) {
            return;
        }

        const offsetX = e.pageX - mapContEl.offsetLeft;  // e.offsetX;
        const offsetY = e.pageY - mapContEl.offsetTop;   // e.offsetY;

        const oldMapCurWidth  = mapCurWidth;
        const oldMapCurHeight = mapCurHeight;

        const offsetXFactor = offsetX / oldMapCurWidth;
        const offsetYFactor = offsetY / oldMapCurHeight;

        const sign = delta > 0 ? 1 : -1;

        mapCurWidth  += sign * (mapCurWidth * zoomStep);
        mapCurHeight += sign * (mapCurHeight * zoomStep);

        mapCurWidth  = Math.max(mapWidth * minZoom, mapCurWidth);
        mapCurHeight = Math.max(mapHeight * minZoom, mapCurHeight);

        mapCurWidth  = Math.min(mapWidth * maxZoom, mapCurWidth);
        mapCurHeight = Math.min(mapHeight * maxZoom, mapCurHeight);

        const diffX = oldMapCurWidth * offsetXFactor - mapCurWidth * offsetXFactor;
        const diffY = oldMapCurHeight * offsetYFactor - mapCurHeight * offsetYFactor;

        mapLeft += diffX;
        mapTop  += diffY;

        mapContEl.style.width  = mapCurWidth + 'px';
        mapContEl.style.height = mapCurHeight + 'px';
        mapContEl.style.left   = mapLeft + 'px';
        mapContEl.style.top    = mapTop + 'px';
    });

    mapContEl.addEventListener('mousedown', (e) => {
        if (isLeftMouseButton(e, true)) {
            isMoving = true;
        }
    });

    document.documentElement.addEventListener('mouseup', (e) => {
        if (isLeftMouseButton(e, false)) {
            isMoving = false;
        }
    });

    document.documentElement.addEventListener('mousemove', (e) => {
        if (isMoving) {
            mapLeft += e.movementX;
            mapTop  += e.movementY;

            mapContEl.style.left = mapLeft + 'px';
            mapContEl.style.top  = mapTop + 'px';
        }
    });

    const updateCategoryMarkers = (category) => {
        const { isActive } = category.stateCategory;

        category.markers.forEach((marker) => {
            if (isActive) {
                marker.el.classList.add('map__marker_active');
            } else {
                marker.el.classList.remove('map__marker_active');                
            }
        });
    };

    const recountCategory = (category) => {
        const { stateCategory } = category;

        if (!category.tip || !stateCategory.hasCollectibles) {
            return;
        }

        const inProgress = category.markers.filter(({ stateMarker }) => {
            return stateMarker.state != MarkerState.Complete;
        });

        category.tip.setContent(`${ stateCategory.title } (${ inProgress.length })`);
    };

    // ------------------------- 

    const categories = [];

    const mapData4 = await fetchMapData();

    mapData4.categories.forEach((stateCategory) => {
        const category = {
            stateCategory,
            markers: [],
            el: null,
            tip: null
        };

        categories.push(category);

        const categoryClass = stateCategory.id.replaceAll('_', '-');

        const buttonEl = document.createElement('button');

        buttonEl.type = 'button';
        buttonEl.className = `panel__button panel__button_${ categoryClass }`;

        if (stateCategory.isActive) {
            buttonEl.classList.add('panel__button_active');            
        }

        buttonEl.addEventListener('click', () => {
            if (stateCategory.isActive) {
                stateCategory.isActive = false;
                buttonEl.classList.remove('panel__button_active');
            } else {                
                stateCategory.isActive = true;
                buttonEl.classList.add('panel__button_active');
            }

            updateCategoryMarkers(category);

            saveMapData(mapData4);
        });

        panelEl.append(buttonEl);

        const buttonTip = tippy(buttonEl, {
            content: stateCategory.title,
            arrow: true,
            placement: 'bottom',
        });

        category.el = buttonEl;
        category.tip = buttonTip;

        stateCategory.markers.forEach((stateMarker) => {
            const markerEl = document.createElement('div');

            markerEl.style.left = (stateMarker.x * 100) + '%';
            markerEl.style.top  = (stateMarker.y * 100) + '%';

            markerEl.className = `map__marker map__marker_${ categoryClass }`;

            if (stateCategory.isActive) {
                markerEl.classList.add('map__marker_active');
            }

            switch (getMarkerState(stateMarker)) {
                case MarkerState.Default:
                    markerEl.classList.add('map__marker_state_default');
                    break;
                case MarkerState.Progress:
                    markerEl.classList.add('map__marker_state_progress');
                    break;
                case MarkerState.Complete:
                    markerEl.classList.add('map__marker_state_complete');
                    break;
            }

            markerEl.addEventListener('contextmenu', (e) => {
                e.preventDefault();

                switch (getMarkerState(stateMarker)) {
                    case MarkerState.Default:
                        stateMarker.state = MarkerState.Progress;
                        markerEl.classList.remove('map__marker_state_default');
                        markerEl.classList.add('map__marker_state_progress');
                        break;
                    case MarkerState.Progress:
                        stateMarker.state = MarkerState.Complete;
                        markerEl.classList.remove('map__marker_state_progress');
                        markerEl.classList.add('map__marker_state_complete');
                        break;
                    case MarkerState.Complete:
                        stateMarker.state = MarkerState.Default;
                        markerEl.classList.remove('map__marker_state_complete');
                        markerEl.classList.add('map__marker_state_default');
                        break;
                }

                recountCategory(category);

                saveMapData(mapData4);
            });

            markersEl.append(markerEl);

            let popupText = ''; 
            let isInteractive = false;

            if (stateMarker.description) {
                if (stateMarker.title) {
                    popupText += `<strong>${ stateMarker.title }</strong><br>`;
                }

                const { description } = stateMarker;

                const converter = new showdown.Converter();

                const descriptionHTML = converter.makeHtml(description);

                popupText += descriptionHTML;

                isInteractive = description !== descriptionHTML;
            } else if (stateMarker.title) {
                popupText = stateMarker.title;
            }

            if (popupText) {
                tippy(markerEl, {
                    content: popupText,
                    arrow: true,
                    placement: 'top',
                    allowHTML: true,
                    interactive: isInteractive,
                    delay: [ 75, 0 ],
                });
            }

            category.markers.push({
                stateMarker,
                el: markerEl
            });

            recountCategory(category);
        });
    });

    // https://atomiks.github.io/tippyjs/v6/all-props/
    tippy(visBtnEl, {
        content: 'Show/hide all',
        arrow: true,
        placement: 'bottom',
    });

    visBtnEl.addEventListener('click', (e) => {
        const activeCats   = categories.filter(c => c.stateCategory.isActive);
        const areAllActive = activeCats.length === categories.length;

        categories.forEach((category) => {
            const { stateCategory } = category;

            stateCategory.isActive = !areAllActive;

            if (stateCategory.isActive) {
                category.el.classList.add('panel__button_active');
            } else {
                category.el.classList.remove('panel__button_active');
            }

            updateCategoryMarkers(category);
        });

        saveMapData(mapData4);
    });
};



/^(interactive|complete)$/.test(document.readyState) ? init() : window.addEventListener('load', init);
