<?php
/*
Template Name: Sunpass Landing
Template Post Type: page, post
*/

add_action('wp_enqueue_scripts', 'enqueueSunpassAssets');

$faqData = fetchFAQ($TNP_FLORIDA_BRAND);

?>
<!doctype html>
<html <?php language_attributes(); ?> <?php getHTMLClasses(); ?>>
<head>
    <title><?php single_post_title(); ?></title>
    <link rel="icon" href="<?php echo getFavicon('tapnpay'); ?>">
    <meta charset="<?php bloginfo('charset'); ?>" />
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script async src="https://tag.simpli.fi/sifitag/951ddf90-4a63-013a-4fc0-06abc14c0bc6"></script>
    <?php require(dirname(__FILE__) . '/common_head.php'); ?>
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>

<?php wp_body_open(); ?>

<!-- /// -->

<div class="panel">
    <div class="panel__inner">
        <a href="<?= getCurrentURL(); ?>" class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1442 420" class="logo__svg">
                <path fill="#8cc540" d="M613.18,181.25h43.19v17.64Q671.06,186.5,683,181.66a64.5,64.5,0,0,1,24.41-4.84q25.59,0,43.44,17.88,15,15.18,15,44.93V353.38H723.13V278q0-30.81-2.77-40.93t-9.62-15.4q-6.87-5.29-17-5.3a31.83,31.83,0,0,0-22.49,8.77q-9.39,8.78-13,24.26-1.89,8.06-1.89,34.92v69.06H613.18Z"/>
                <path fill="#1a5d89" d="M32.32,117.34H54.47v63.91H89.59v19.14H54.47v153H32.32v-153H2.11V181.25H32.32Zm262,63.91V353.38H272.48V323.79q-13.94,16.93-31.25,25.47a84.43,84.43,0,0,1-37.89,8.55q-36.54,0-62.41-26.5t-25.87-64.47q0-37.17,26.11-63.6T204,176.82q21.21,0,38.37,9t30.14,27V181.25Zm-88.52,16.93a66.81,66.81,0,0,0-59,34.61,69.76,69.76,0,0,0,.08,69.53,67.91,67.91,0,0,0,25.05,25.83,65.36,65.36,0,0,0,33.74,9.25,69.14,69.14,0,0,0,34.44-9.17,64.12,64.12,0,0,0,25-24.81q8.78-15.65,8.77-35.24,0-29.85-19.67-49.93T205.79,198.18Zm138.67-16.93h22.15v31.64q13.11-18,30.18-27a80.3,80.3,0,0,1,38.09-9q36.66,0,62.74,26.42t26.08,63.6q0,38-25.84,64.47t-62.35,26.5a83.8,83.8,0,0,1-37.77-8.55q-17.22-8.53-31.13-25.47v92.55H344.46Zm88.59,16.93q-28.73,0-48.38,20.07T365,268.18q0,19.6,8.76,35.24a63.83,63.83,0,0,0,25.09,24.81,69.46,69.46,0,0,0,34.49,9.17,65,65,0,0,0,33.54-9.25,67.84,67.84,0,0,0,25-25.83,69.79,69.79,0,0,0,.07-69.53,66.68,66.68,0,0,0-58.95-34.61ZM687,97.5c-33.87,0-64.94,23.2-89.24,61.87,25.39-30.2,56.12-47.87,89.24-47.87s63.85,17.67,89.24,47.87C751.94,120.7,720.87,97.5,687,97.5Z"/>
                <path fill="#25a8e0" d="M850.34,181.25h22.15v31.64q13.11-18,30.19-27a80.23,80.23,0,0,1,38.08-9q36.68,0,62.75,26.42t26.07,63.6q0,38-25.84,64.47t-62.34,26.5a83.82,83.82,0,0,1-37.78-8.55q-17.22-8.53-31.13-25.47v92.55H850.34Zm88.59,16.93q-28.73,0-48.37,20.07t-19.65,49.93q0,19.6,8.76,35.24a63.9,63.9,0,0,0,25.09,24.81,69.46,69.46,0,0,0,34.49,9.17,65,65,0,0,0,33.54-9.25,67.84,67.84,0,0,0,25-25.83,69.79,69.79,0,0,0,.07-69.53,66.68,66.68,0,0,0-59-34.61Zm303.6-16.93V353.38h-21.84V323.79q-13.92,16.93-31.24,25.47a84.43,84.43,0,0,1-37.89,8.55q-36.54,0-62.41-26.5t-25.87-64.47q0-37.17,26.1-63.6t62.81-26.42q21.19,0,38.37,9t30.13,27V181.25ZM1154,198.18a66.81,66.81,0,0,0-59,34.61,69.76,69.76,0,0,0,.08,69.53,67.82,67.82,0,0,0,25,25.83,65.39,65.39,0,0,0,33.74,9.25,69.15,69.15,0,0,0,34.45-9.17,64.12,64.12,0,0,0,25-24.81q8.76-15.65,8.77-35.24,0-29.85-19.68-49.93T1154,198.18Zm119.84-16.93h23.41l59.16,132.55,57.44-132.55h23.57L1334.76,416.34h-23.4l33.14-76ZM687,50.5c-47.78,0-91.1,30-122.67,78.6C598,91.8,640.62,69.5,687,69.5s89,22.3,122.67,59.6C778.1,80.49,734.78,50.5,687,50.5Z"/>
                <path fill="#f69320" d="M861.53,125.57C820.28,63.89,757.41,24.5,687,24.5S553.72,63.89,512.47,125.57C550.16,52.25,614.26,4,687,4S823.84,52.25,861.53,125.57Z"/>
            </svg>
        </a>
        <button type="button" class="nav-switcher">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="12" class="svg">
                <path d="M0 0h18v2H0zM0 5h18v2H0zM0 10h18v2H0z"></path>
            </svg>
        </button>
        <nav class="nav">
            <div class="nav__overlay"></div>
            <div class="nav__panel">
                <button type="button" class="nav__hide">
                    <i class="icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" class="svg">
                            <path d="M10.42 9l7.07 7.07-1.42 1.42L9 10.42l-7.07 7.07-1.42-1.42L7.58 9 .51 1.93 1.93.51 9 7.58 16.07.51l1.42 1.42L10.42 9z"></path>
                        </svg>
                    </i>
                </button>
                <div class="nav__scroll" role="navigation">
                    <ul class="nav__list nav__list_underlined">
                        <li><a href="#how_it_works" class="nav__link nav__link_underlined">How It Works</a></li>
                        <?php if (false): ?>
                        <li><a href="#testimonials" class="nav__link nav__link_underlined">Testimonials</a></li>
                        <?php endif; ?>
                        <li><a href="#faq" class="nav__link nav__link_underlined">FAQ</a></li>
                        <li><a href="#contact_us" class="nav__link nav__link_underlined">Contact Us</a></li>
                        <li><a href="#get_started" class="nav__link nav__link_underlined">Get Started</a></li>
                        <!--<li>
                            <?php /*echo do_shortcode('[language-switcher]');*/ ?>
                        </li>-->
                    </ul>
                </div>
            </div>
        </nav>
        <div class="language-switcher">
            <button type="button" class="language-switcher__button">
                <span class="language-switcher__current_language">En</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="8" class="language-switcher__triangle">
                    <path fill="currentColor" d="M6,7.207,1.293,2.5A1,1,0,1,1,2.707,1.0859L6,4.3789l3.293-3.293A1,1,0,1,1,10.707,2.5Z"></path>
                </svg>
            </button>
            <div class="language-switcher__popup">
                <ul class="language-switcher__list">
                    <li class="language-switcher__item" data-code="en" data-short-name="En">English</li>
                    <li class="language-switcher__item" data-code="es" data-short-name="Es">Spanish</li>
                </ul>
            </div>
        </div>
    </div>
</div>

<section class="section-main">
    <div class="section-main__bg">
        <div class="section-main__content">
            <div class="section-main__text">
                <h1 class="section-main__text-header">Paying Florida SunPass tolls just got easier</h1>
                <div class="section-main__text-description">
                    In three quick and easy steps, you will be on your way to using SunPass toll roads, without requiring a toll tag. Save $5 with free registration until March 15, 2022
                </div>
            </div>
            <div class="section-main__form">
                <div class="section-main__form-content">
                    <div class="section-main__form-header">Provide your phone number and get started!</div>
                    <div class="section-main__form-inputs">
                        <?php $phoneFormStyleClass = ''; ?>
                        <?php require(dirname(__FILE__) . '/sunpass_phone_form.php'); ?>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="section-points">
    <div class="section-points__item">
        <div class="section-points__item-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80" class="svg">
                <path fill="currentColor" d="M40,3A37,37,0,1,1,3,40,37,37,0,0,1,40,3Zm0-3A40,40,0,1,0,80,40,40,40,0,0,0,40,0ZM62.24,58.61c.52-.62,1-1.28,1.5-2a1.5,1.5,0,1,0-2.45-1.73c-.43.61-.88,1.2-1.35,1.76a26,26,0,0,1-39.88,0q-.76-.91-1.44-1.89a1.5,1.5,0,0,0-2.46,1.72c.5.71,1,1.42,1.6,2.1a29,29,0,0,0,44.48,0ZM18.74,25a26,26,0,0,1,42.52,0,1.49,1.49,0,0,0,2.09.36,1.51,1.51,0,0,0,.36-2.09,29,29,0,0,0-47.42,0,1.5,1.5,0,0,0,.36,2.09,1.53,1.53,0,0,0,.86.27A1.49,1.49,0,0,0,18.74,25ZM64.5,46H59V42h2.5a1.5,1.5,0,0,0,0-3H59V35h5.5a1.5,1.5,0,0,0,0-3h-7A1.5,1.5,0,0,0,56,33.5v14A1.5,1.5,0,0,0,57.5,49h7a1.5,1.5,0,0,0,0-3Zm-14,0H45V42h2.5a1.5,1.5,0,0,0,0-3H45V35h5.5a1.5,1.5,0,0,0,0-3h-7A1.5,1.5,0,0,0,42,33.5v14A1.5,1.5,0,0,0,43.5,49h7a1.5,1.5,0,0,0,0-3Zm-11.94.44L34,41.9A5,5,0,0,0,33,32H29.5A1.5,1.5,0,0,0,28,33.5v14a1.5,1.5,0,0,0,3,0V43.12l5.44,5.44a1.5,1.5,0,0,0,2.12-2.12ZM31,35h2a2,2,0,0,1,0,4H31Zm-8.5-3h-7A1.5,1.5,0,0,0,14,33.5v14a1.5,1.5,0,0,0,3,0V42h2.5a1.5,1.5,0,0,0,0-3H17V35h5.5a1.5,1.5,0,0,0,0-3Z"/>
            </svg>
        </div>
        <div class="section-points__item-text">
            <div class="section-points__item-header">Simple and free Registration</div>
            <div class="section-points__item-description">
                For a limited time, you can register for tapNpay for free. After that, registration cost is a one-time fee of $5.00 per license plate
            </div>
        </div>
    </div>
    <div class="section-points__item">
        <div class="section-points__item-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80" class="svg">
                <path fill="currentColor" d="M72,14H68.24l9.38-9.38L75.5,2.5,64,14H8a8,8,0,0,0-8,8V56a8,8,0,0,0,8,8h6L2.5,75.5l2.12,2.12L18.24,64H72a8,8,0,0,0,8-8V22A8,8,0,0,0,72,14Zm0,3a5,5,0,0,1,5,5v2H58.24l7-7Zm5,16H49.24l6-6H77ZM3,27H51l-6,6H3Zm0-5a5,5,0,0,1,5-5H61l-7,7H3ZM8,61a5,5,0,0,1-5-5V36H42L17,61Zm69-5a5,5,0,0,1-5,5H21.24l25-25H77Z"/>
            </svg>
        </div>
        <div class="section-points__item-text">
            <div class="section-points__item-header">No Toll Transponder Required</div>
            <div class="section-points__item-description">
                tapNpay makes it easy to pay tolls, without needing a toll transponder/tag. Just register, drive the toll roads, approve your invoice and we take care of the rest
            </div>
        </div>
    </div>
    <div class="section-points__item">
        <div class="section-points__item-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80" class="svg">
                <path fill="currentColor" d="M52,18a33.3,33.3,0,0,0-7,.74V8a8,8,0,0,0-8-8H10A8,8,0,0,0,2,8V72a8,8,0,0,0,8,8H37a8,8,0,0,0,8-8V57.27A33.8,33.8,0,0,0,52,58c14.34,0,26-9,26-20S66.34,18,52,18ZM5,8a5,5,0,0,1,5-5H37a5,5,0,0,1,5,5v2H5ZM42,72a5,5,0,0,1-5,5H10a5,5,0,0,1-5-5V69H42Zm0-6H5V13H42v6.54C32.61,22.56,26,29.7,26,38a16.76,16.76,0,0,0,4.08,10.81c-.37,2.06-.83,5.2-1,6.77a3,3,0,0,0,3.7,3.33s3.42-.85,9.27-2ZM52,55a30.51,30.51,0,0,1-7-.8c-.69-.16-1.36-.34-2-.55l-1,.19C35.62,55.09,32,56,32,56s1-7,1.33-8.07A14.18,14.18,0,0,1,29,38c0-6.74,5.31-12.56,13-15.31a26.06,26.06,0,0,1,3-.89,30.58,30.58,0,0,1,7-.8c12.7,0,23,7.61,23,17S64.7,55,52,55ZM26.5,8h-6A1.5,1.5,0,0,1,19,6.5h0A1.5,1.5,0,0,1,20.5,5h6A1.5,1.5,0,0,1,28,6.5h0A1.5,1.5,0,0,1,26.5,8ZM26,73a2,2,0,1,1-2-2A2,2,0,0,1,26,73ZM55,38a2,2,0,1,1-2-2A2,2,0,0,1,55,38Zm8,0a2,2,0,1,1-2-2A2,2,0,0,1,63,38ZM47,38a2,2,0,1,1-2-2A2,2,0,0,1,47,38Z"/>
            </svg>
        </div>
        <div class="section-points__item-text">
            <div class="section-points__item-header">Pay your tolls on your mobile using text</div>
            <div class="section-points__item-description">
                Simply drive the SunPass toll roads, approve daily charges via SMS/Text, and pay using your payment choice (and there a lots to choose from)
            </div>
        </div>
    </div>
</section>

<section class="section-steps" id="how_it_works">
    <h2 class="section-header">See How It Works</h2>
    <div class="section-subheader">Once you register your vehicles license plate, your tolls can be charged to either Apple Pay, Google Pay, Credit or Debit card, or PayPal/Venmo. If you can text on your phone, you can pay on your phone! Registering from your phone is simple, takes only a few minutes and until March 15, 2022, it’s free to join</div>
    <div class="section-steps__items">
        <div class="section-steps__card">
            <img class="section-steps__card-image" src="<?php echo (get_template_directory_uri() . '/assets/images/sunpass/step_1.svg') ?>" alt="Step 1">
            <div class="section-steps__card-header">Register</div>
            <div class="section-steps__card-description">Sign up for free – select your toll payment method of choice, and you’re on your way</div>
        </div>
        <div class="section-steps__arrow"></div>
        <div class="section-steps__card">
            <img class="section-steps__card-image" src="<?php echo (get_template_directory_uri() . '/assets/images/sunpass/step_2.svg') ?>" alt="Step 2">
            <div class="section-steps__card-header">Drive</div>
            <div class="section-steps__card-description">It’s time to hit the road! After you’ve completed your registration, simple drive any Florida SunPass toll road (except around Orlando) and receive a text notification to approve your daily transaction</div>
        </div>
        <div class="section-steps__arrow"></div>
        <div class="section-steps__card">
            <img class="section-steps__card-image" src="<?php echo (get_template_directory_uri() . '/assets/images/sunpass/step_3.svg') ?>" alt="Step 3">
            <div class="section-steps__card-header">Approve</div>
            <div class="section-steps__card-description">Review your toll charges and approve them. Then select the payment method, and you’re done. Easy Peasy.</div>
        </div>
    </div>
</section>

<?php if (false): ?>
<section class="section-testimonials" id="testimonials">
    <h2 class="section-header">Testimonials</h2>
    <div class="section-testimonials__items">
        <div class="section-testimonials__item">
            <div class="section-testimonials__item-content">
                <div class="section-testimonials__item-text">
                    I was traveling in Miami and didn't have a SunPass tag. I wanted to avoid getting a paper invoice which is a hassle to deal with,  so I joined  tapNpay in less than 2 minutes. Great payment tool.
                </div>
                <div class="section-testimonials__item-sign">
                    — Steve Smith, Las Vegas, Nevada
                </div>
            </div>
        </div>
        <div class="section-testimonials__item">
            <div class="section-testimonials__item-content">
                <div class="section-testimonials__item-text">
                    I'd been shopping and I had a call to get back to the office ASAP. I needed to use the toll road to save time. As I am not a frequent toll road user I decided to use  tapNpay to pay my toll. It was easy and convenient.
                </div>
                <div class="section-testimonials__item-sign">
                    — Susan Stone, Tampa, Florida
                </div>
            </div>
        </div>
        <div class="section-testimonials__item">
            <div class="section-testimonials__item-content">
                <div class="section-testimonials__item-text">
                    I was visiting from Dallas where I use tapNpay to pay my NTTA tolls. What a pleasure to see I could use it in Florida on the  SunPass roads as well.  
                </div>
                <div class="section-testimonials__item-sign">
                    — Sarah Bubkis, Dallas, Texas
                </div>
            </div>
        </div>
    </div>    
</section>
<?php endif; ?>

<?php if ($faqData): ?>
<section class="section-faq" id="faq">
    <h2 class="section-header">FAQ</h2>
    <div class="section-faq__items">
        <?php 
            foreach ($faqData as $faqCategory):
                foreach ($faqCategory['items'] as $faqItem):
        ?>
            <div class="section-faq__item">
                <div class="section-faq__item-main">
                    <div class="section-faq__item-q">
                        <?= $faqItem['question']; ?>
                    </div>
                </div>
                <div class="section-faq__item-a">
                    <?= $faqItem['answer']; ?>
                </div>
            </div>
        <?php 
                endforeach;
            endforeach; 
        ?>
    </div>    
</section>
<?php endif; ?>

<section class="section-feedback" id="contact_us">
    <h2 class="section-header">Contact Us</h2>
    <div class="section-subheader">Our staff is here when you need us. Whether you have questions on how to subscribe to tapNpay or questions on your invoice.</div>
    <div class="section-feedback__content">
        <div class="section-feedback__message"></div>
        <fieldset class="section-feedback__fieldset">            
            <form method="POST" action="/" class="section-feedback__form">
                <input type="text" class="input section-feedback__input" data-error-class="input_has-error" name="first_name" placeholder="First name" required>
                <input type="text" class="input section-feedback__input" data-error-class="input_has-error" name="last_name" placeholder="Last name" required>
                <input type="email" class="input section-feedback__input" data-error-class="input_has-error" name="email" placeholder="Email" required>
                <input type="tel" class="input section-feedback__input" data-error-class="input_has-error" name="phone" placeholder="Phone number" required>
                <textarea class="textarea section-feedback__textarea" data-error-class="textarea_has-error" name="comment" placeholder="Your question" required></textarea>
                <input type="hidden" name="brand" value="SUNPASS">
                <button type="submit" class="button button_blue section-feedback__button">
                    <span class="button__caption">Get Started</span>
                    <span class="button__spinner">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28">
                            <path d="M14,27A13,13,0,1,1,27,14,13.0144,13.0144,0,0,1,14,27ZM14,3A11,11,0,1,0,25,14,11.0125,11.0125,0,0,0,14,3Z" style="fill: currentColor; opacity: 0.2;"></path>
                            <path d="M6.52,24.6333A13.0008,13.0008,0,0,1,14,1V3A11.0007,11.0007,0,0,0,7.6719,22.9985Z" style="fill: currentColor;"></path>
                        </svg>
                    </span>
                </button>
            </form>
        </fieldset>
    </div>
</section>

<section class="section-getting-started" id="get_started">
    <h2 class="section-header">Why use tapNpay</h2>
    <div class="section-getting-started__content">
        <div class="section-getting-started__palm"></div> 
        <div class="section-getting-started__text">
            <p>We’ve created a new mobile payment option to make Florida SunPass toll payments more convenient and accessible for pay-by-mail customers. Register your license plate number through SMS/Text, answer a few questions, drive the roads, approve daily charges (via text), and pay by your favorite method (Apple Pay, Google Pay, Credit Card, Debit Card, PayPal or Venmo). The service normally costs $5.00 one-time registration fee to join, but we’re waiving that fee until March 15, 2022, so make sure to take advantage of this special offer right away.</p>
            <p>All you need to get started is a phone that can text, and any of the payment methods we offer. Then voila, your ready to drive the Florida SunPass roads right away!</p> 
        </div> 
        <div class="section-getting-started__form">    
            <?php $phoneFormStyleClass = 'phone-form_white'; ?>
            <?php require(dirname(__FILE__) . '/sunpass_phone_form.php'); ?>
        </div>     
    </div>
</section>

<footer class="footer">
    <div class="footer__content">
        <div class="footer__item">
            <div class="footer__copyright">Copyright © <?php the_time('Y'); ?> tapNpay Inc. All rights reserved</div>
        </div>
        <!--<div class="footer__item footer__item_right">
            <a href="#" class="footer__link">Terms & Conditions</a>
        </div>-->
        <div class="footer__item footer__item_right">
            <a href="<?= getSunpassPrivacyPolicyURL(); ?>" class="footer__link">Privacy Policy</a>
        </div>        
    </div>
</footer>

<?php wp_footer(); ?>

</body>
</html>
