<?php

$TNP_FLORIDA_BRAND = 'SUNPASS';
$TNP_CALIFORNIA_BRAND = 'FASTRAK';

function getHTMLClasses () {
	$classes = apply_filters('tnp_the_html_classes', '');

	if (!$classes) {
		return;
	}

	echo 'class="' . esc_attr($classes) . '"';
}

function getAssetModificationTime ($path) {
    $time = filemtime(get_template_directory() . $path);
    return $time ? $time : 0;
}

function getFavicon ($page) {
    $path = '/assets/images/' . $page . '/favicon.ico';
    return get_template_directory_uri() . $path . '?rnd=' . strval(getAssetModificationTime($path));
}

function enqueueAsset ($type, $name, $path, $inline = null) {
    $rndName = $name . '?rnd=' . strval(getAssetModificationTime($path));
    $url = get_template_directory_uri() . $path;

    switch ($type) {
        case 'css':
            wp_enqueue_style($rndName, $url);
            break;
        case 'js':
            wp_enqueue_script($rndName, $url);

            if ($inline) {
                foreach ($inline as $item) {
                    wp_add_inline_script($name, $item[1], $item[0]);
                }
            }

            break;
    }
}

function getConfig () {
    $isDev = isDev();

    return array(
        'isLoggedIn' => is_user_logged_in(),
        'phoneFormURL' => ($isDev ? 'https://mock-app.oriondev.org/acquisition/web-sms' : 'https://app.tapnpay.biz/acquisition/web-sms'),
        'phoneFormBrand' => null,
        'feedbackFormURL' => ($isDev ? 'https://mock-app.oriondev.org/contact-us' : 'https://app.tapnpay.biz/contact-us'),
        'recaptchaSiteKey' => '6LfK6QscAAAAAHVNdEwx5qH_uhYBzAEuR3oqMiN8'
    );
}

function enqueueTapnpayAssets () {
    enqueueAsset('js', 'tnp_landing', '/assets/js/tapnpay.js', array(
        array('before', 'window.tnpConfig = ' . json_encode(getConfig())),
    ));
    enqueueAsset('css', 'tnp_landing', '/assets/css/tapnpay.css');
}

function enqueueSunpassAssets () {
    global $TNP_FLORIDA_BRAND;

    $config = getConfig();
    $config['phoneFormBrand'] = $TNP_FLORIDA_BRAND;

    enqueueAsset('js', 'sunpass_landing', '/assets/js/sunpass.js', array(
        array('before', 'window.sunpassConfig = ' . json_encode($config)),
    ));
    enqueueAsset('css', 'sunpass_landing', '/assets/css/sunpass.css');
}

function enqueueSunpassPrivacyPolicyAssets () {
    enqueueAsset('js', 'sunpass_privacy_policy', '/assets/js/sunpass_privacy_policy.js');
    enqueueAsset('css', 'sunpass_privacy_policy', '/assets/css/sunpass_privacy_policy.css');
}

function enqueueFastrakAssets () {
    global $TNP_CALIFORNIA_BRAND;    
    
    $config = getConfig();
    $config['phoneFormBrand'] = $TNP_CALIFORNIA_BRAND;

    enqueueAsset('js', 'fastrak_landing', '/assets/js/fastrak.js', array(
        array('before', 'window.fastrakConfig = ' . json_encode($config)),
    ));
    enqueueAsset('css', 'fastrak_landing', '/assets/css/fastrak.css');
}

function enqueueFastrakPrivacyPolicyAssets () {
    enqueueAsset('js', 'fastrak_privacy_policy', '/assets/js/fastrak_privacy_policy.js');
    enqueueAsset('css', 'fastrak_privacy_policy', '/assets/css/fastrak_privacy_policy.css');
}

function enqueueNotFoundAssets () {
    enqueueAsset('js', 'not_found', '/assets/js/not_found.js');
    enqueueAsset('css', 'not_found', '/assets/css/not_found.css');
}

function getCurrentLang () {
    global $TRP_LANGUAGE;

    return strtolower(preg_split('/[-_]/', $TRP_LANGUAGE)[0]);
}

function fetchFAQ ($brand) {
    $lang = getCurrentLang();
    $supportedLangs = array('en', 'es');

    if (!in_array($lang, $supportedLangs)) {
        $lang = $supportedLangs[0];
    }

    $curl = curl_init();

    curl_setopt($curl, CURLOPT_URL, 'https://app.tapnpay.biz/faq?lang=' . $lang . '&brand=' . $brand);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);

    $result = curl_exec($curl);
    $status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

    if ($status >= 200 && $status < 400) {
        return json_decode($result, true)['categories'];
    } else {
        return null;
    }
}

function getCurrentURL () {
    global $wp;
    return home_url($wp->request);
}

function getPageURLBySlug ($slug) {
    $page = get_page_by_path($slug);

    if ($page == null) {
        return null;
    }

    $pagePermalink = get_permalink($page);

    return $pagePermalink ? $pagePermalink : null;
}

function getSunpassPageURL () {
    return getPageURLBySlug('sunpass');
}

function getSunpassPrivacyPolicyURL () {
    return getPageURLBySlug('sunpass-privacy-policy');
}

function getFastrakPageURL () {
    return getPageURLBySlug('fastrak');
}

function getFastrakPrivacyPolicyURL () {
    return getPageURLBySlug('fastrak-privacy-policy');
}

function isDev () {
    $devHosts = array('tnpinfo.local', 'localhost', '127.0.0.1');
    $buildMode = isset($_GET['buildmode']) ? $_GET['buildmode'] : null;


    return isset($_SERVER['HTTP_HOST']) && in_array($_SERVER['HTTP_HOST'], $devHosts) && $buildMode != 'prod' || $buildMode == 'dev';
}

function printVar ($var) {    
    echo '<pre>';
    var_dump($var);
    echo '</pre>';
}

function endsWith ($haystack, $needle) {
    $length = strlen($needle);

    if (!$length) {
        return true;
    }

    return substr($haystack, -$length) === $needle;
}

function redirectNTTA () {
    $referer = $_SERVER['HTTP_REFERER'];

    if (!$referer) {
        return;
    }

    $host = parse_url($referer, PHP_URL_HOST);

    if (!$host) {
        return;
    }

    if (endsWith(strtolower($host), 'ntta.org')) {
        header('Location: /get-started');
        die();
    }
}