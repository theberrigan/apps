const init = () => {
};
/^(interactive|complete)$/.test(document.readyState) ? init() : window.addEventListener('load', init);
