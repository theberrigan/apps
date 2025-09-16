<?php

add_action('wp_enqueue_scripts', 'enqueueNotFoundAssets');

?>
<!doctype html>
<html <?php language_attributes(); ?> <?php getHTMLClasses(); ?>>
<head>
    <title>Page not found</title>
    <link rel="icon" href="<?php echo getFavicon('tapnpay'); ?>">
    <meta charset="<?php bloginfo('charset'); ?>" />
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <?php require(dirname(__FILE__) . '/common_head.php'); ?>
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>

<?php wp_body_open(); ?>

<!-- /// -->

<div class="message">404</div>

<!-- /// -->

<?php wp_footer(); ?>

</body>
</html>
