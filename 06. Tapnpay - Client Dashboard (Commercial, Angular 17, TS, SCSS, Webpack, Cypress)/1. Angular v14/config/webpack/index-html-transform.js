module.exports = async (targetOptions, indexHtmlContent) => {
    if (targetOptions.configuration === 'production') {   // development
        const gaCode = (
            `\n<script async src="https://www.googletagmanager.com/gtag/js?id=UA-140683828-2"></script>
            <script>
                window.dataLayer = window.dataLayer || [];

                function gtag () {
                    dataLayer.push(arguments);
                }

                gtag('js', new Date());
                gtag('config', 'UA-140683828-2');
            </script>`
        );

        indexHtmlContent = indexHtmlContent.replace(/<\/head>/i, gaCode + '\n</head>');
    }

    return indexHtmlContent;
};
