<?php
/*
Template Name: FasTrak Privacy Policy
*/

add_action('wp_enqueue_scripts', 'enqueueFastrakPrivacyPolicyAssets');

?>
<!doctype html>
<html <?php language_attributes(); ?> <?php getHTMLClasses(); ?>>
<head>
    <title><?php single_post_title(); ?></title>
    <link rel="icon" href="<?php echo getFavicon('tapnpay'); ?>">
    <meta charset="<?php bloginfo('charset'); ?>" />
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script async src="https://tag.simpli.fi/sifitag/e1268380-5a17-013a-9aff-06b4c2516bae"></script>
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>

<?php wp_body_open(); ?>

<!-- /// -->

<div class="panel">
    <div class="panel__content">
        <a href="<?= getFastrakPageURL(); ?>" class="panel__logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1442 420" class="panel__logo-svg">
                <path fill="#8cc540" d="M613.18,181.25h43.19v17.64Q671.06,186.5,683,181.66a64.5,64.5,0,0,1,24.41-4.84q25.59,0,43.44,17.88,15,15.18,15,44.93V353.38H723.13V278q0-30.81-2.77-40.93t-9.62-15.4q-6.87-5.29-17-5.3a31.83,31.83,0,0,0-22.49,8.77q-9.39,8.78-13,24.26-1.89,8.06-1.89,34.92v69.06H613.18Z"/>
                <path fill="#1a5d89" d="M32.32,117.34H54.47v63.91H89.59v19.14H54.47v153H32.32v-153H2.11V181.25H32.32Zm262,63.91V353.38H272.48V323.79q-13.94,16.93-31.25,25.47a84.43,84.43,0,0,1-37.89,8.55q-36.54,0-62.41-26.5t-25.87-64.47q0-37.17,26.11-63.6T204,176.82q21.21,0,38.37,9t30.14,27V181.25Zm-88.52,16.93a66.81,66.81,0,0,0-59,34.61,69.76,69.76,0,0,0,.08,69.53,67.91,67.91,0,0,0,25.05,25.83,65.36,65.36,0,0,0,33.74,9.25,69.14,69.14,0,0,0,34.44-9.17,64.12,64.12,0,0,0,25-24.81q8.78-15.65,8.77-35.24,0-29.85-19.67-49.93T205.79,198.18Zm138.67-16.93h22.15v31.64q13.11-18,30.18-27a80.3,80.3,0,0,1,38.09-9q36.66,0,62.74,26.42t26.08,63.6q0,38-25.84,64.47t-62.35,26.5a83.8,83.8,0,0,1-37.77-8.55q-17.22-8.53-31.13-25.47v92.55H344.46Zm88.59,16.93q-28.73,0-48.38,20.07T365,268.18q0,19.6,8.76,35.24a63.83,63.83,0,0,0,25.09,24.81,69.46,69.46,0,0,0,34.49,9.17,65,65,0,0,0,33.54-9.25,67.84,67.84,0,0,0,25-25.83,69.79,69.79,0,0,0,.07-69.53,66.68,66.68,0,0,0-58.95-34.61ZM687,97.5c-33.87,0-64.94,23.2-89.24,61.87,25.39-30.2,56.12-47.87,89.24-47.87s63.85,17.67,89.24,47.87C751.94,120.7,720.87,97.5,687,97.5Z"/>
                <path fill="#25a8e0" d="M850.34,181.25h22.15v31.64q13.11-18,30.19-27a80.23,80.23,0,0,1,38.08-9q36.68,0,62.75,26.42t26.07,63.6q0,38-25.84,64.47t-62.34,26.5a83.82,83.82,0,0,1-37.78-8.55q-17.22-8.53-31.13-25.47v92.55H850.34Zm88.59,16.93q-28.73,0-48.37,20.07t-19.65,49.93q0,19.6,8.76,35.24a63.9,63.9,0,0,0,25.09,24.81,69.46,69.46,0,0,0,34.49,9.17,65,65,0,0,0,33.54-9.25,67.84,67.84,0,0,0,25-25.83,69.79,69.79,0,0,0,.07-69.53,66.68,66.68,0,0,0-59-34.61Zm303.6-16.93V353.38h-21.84V323.79q-13.92,16.93-31.24,25.47a84.43,84.43,0,0,1-37.89,8.55q-36.54,0-62.41-26.5t-25.87-64.47q0-37.17,26.1-63.6t62.81-26.42q21.19,0,38.37,9t30.13,27V181.25ZM1154,198.18a66.81,66.81,0,0,0-59,34.61,69.76,69.76,0,0,0,.08,69.53,67.82,67.82,0,0,0,25,25.83,65.39,65.39,0,0,0,33.74,9.25,69.15,69.15,0,0,0,34.45-9.17,64.12,64.12,0,0,0,25-24.81q8.76-15.65,8.77-35.24,0-29.85-19.68-49.93T1154,198.18Zm119.84-16.93h23.41l59.16,132.55,57.44-132.55h23.57L1334.76,416.34h-23.4l33.14-76ZM687,50.5c-47.78,0-91.1,30-122.67,78.6C598,91.8,640.62,69.5,687,69.5s89,22.3,122.67,59.6C778.1,80.49,734.78,50.5,687,50.5Z"/>
                <path fill="#f69320" d="M861.53,125.57C820.28,63.89,757.41,24.5,687,24.5S553.72,63.89,512.47,125.57C550.16,52.25,614.26,4,687,4S823.84,52.25,861.53,125.57Z"/>
            </svg>
        </a>    
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

<main class="privacy-policy">
    <div class="privacy-policy__content translation-block">
        <h1>TAPNPAY Privacy Policy</h1>
        <p>TAPNPAY and its affiliates ("<strong>TAPNPAY</strong>", "<strong>we</strong>", "<strong>our</strong>", and/or "<strong>us</strong>") value the privacy of individuals who use our services (collectively, our "<strong>Services</strong>"). This privacy policy ("<strong>Privacy Policy</strong>") explains how we collect, use, and share information from tapNpay users ("<strong>Users,</strong>" "<strong>your</strong>" and/or "<strong>you</strong>"). By using our Services, you agree to the collection, use, disclosure, and procedures this Privacy Policy describes. Beyond the Privacy Policy, your use of our Services is also subject to our Terms and Conditions.</p>

        <h3>Information We Collect</h3>
        <p>We may collect a variety of information from or about you from various sources, as described below.</p>
        <p>If you do not provide your information when requested, you may not be able to use our Services if that information is necessary to provide you with our Services or if we are legally required to collect it.</p>
        <ol class="list list_letter">
            <li><strong>Information You Provide to Us.</strong>
                <ul class="list list_dot">
                    <li><strong>Registration and Profile Information</strong>. Our Services allow you to pay toll charges owed to operators of associated toll facilities ("<strong>ATFOs</strong>") using a Payment Method chosen by you during Account Registration. When you register to use our Services, we may receive your address, your mobile phone number from an eligible Carrier, email address, and your vehicle's license plate numbers ("<strong>LPNs</strong>"), depending on your form of registration. Additionally, you may provide us with toll transaction and travel information. If you are unable to enroll in our Services because the information you provide does not match the information maintained by the ATFO, we may maintain any information that you provide, including your mobile phone number, and use this information for any purposes including business and marketing purposes unless you choose to opt-out as permitted by this Privacy Policy.</li>
                    <li><strong>Payment Information</strong>. When you use our Services to make payments, we allow you to select from several Payment Methods including but not limited to; Apple Pay, Google Pay, Debit Cards, Credit Cards, and PayPal. We do not collect or store any credit card information on our servers.</li>
                    <li><strong>Communications</strong>. If you contact us directly, we may receive additional information about you. For example, when you contact us for customer support, we may receive your name, email address, phone number, the contents of any messages or attachments that you may send to us, and other information you choose to provide.</li>
                </ul>
            </li>
            <li><strong>Information We Collect When You Use Our Services.</strong>
                <ul class="list list_dot">
                    <li><strong>Device Information.</strong> We receive information about the device and software you use to access our Services, including internet protocol ("<strong>IP</strong>") address.</li>
                    <li><strong>Usage Information.</strong> To help us understand how you use our Services and to help us improve them, when you use our Services, we automatically receive information about your interactions with our Services, like the pages or other content you view, pages you request, the websites you visited before using our Services, and the dates, times and durations of your visits.</li>
                    <li><strong>Location Information.</strong> When you use our Services, we infer the general physical location of your device and the geographic regions of our Users. For example, your IP address may indicate your general geographic region.</li>
                    <li><strong>Information from Cookies and Similar Technologies.</strong> We and third-party partners collect information using cookies, pixel tags, or similar technologies. Our third-party partners, such as analytics and advertising partners, may use these technologies to collect information about your online activities over time and across different services. Cookies are small text files containing a string of alphanumeric characters. We may use both session cookies and persistent cookies. A session cookie disappears after you close your browser. A persistent cookie remains after you close your browser and may be used by your browser on subsequent visits to our Services.<br><br>
                        Please review your web browser's "Help" file to learn the proper way to modify your cookie settings. Please note that if you delete or choose not to accept cookies from our Services, you may not be able to utilize the features of our Services to their fullest potential.</li>
                </ul>
            </li>
            <li><strong>Information We Receive from Third Parties</strong>
                <ul class="list list_dot">
                    <li><strong>Associated Toll Facility Operators.</strong> Our Services are operated pursuant to an arrangement we have with the applicable ATFO. By using our Services, you agree that we may receive the following information concerning you, your vehicle, or your account from the applicable ATFO: toll transactions, license plate number and state, billing invoices, location of the toll collection device where charges were incurred, and other information relevant to the provision of our Services. If we receive from an ATFO any information that you have not otherwise provided to us regarding (a) motor vehicle registration or (b) other information derived from a license plate on a vehicle using an ATFO toll facility, that information will not be used by us or, if we disclose or make it available to the applicable ATFO, our vendors, service providers, or billing entities, by such entities for purposes other than: (1) the provision of our Services; (2) toll collection and toll collection enforcement; (3) law enforcement purposes on request by a law enforcement agency; and (4) as otherwise provided for under this Privacy Policy.</li>
                    <li><strong>Other Third Parties.</strong> We may receive additional information about you from third parties such as data or marketing partners and combine it with other information we have about you.</li>
                </ul>
            </li>
        </ol>

        <h3>How We Use the Information We Collect</h3>
        <p>We use the information you provide to us or that we collect when you use our Services:</p>
        <ul class="list list_dot">
            <li>To provide, maintain, improve, develop, and enhance our products and services;</li>
            <li>To understand and analyze how you use our Services and develop new products, services, features, and functionality;</li>
            <li>To communicate with you, provide you with updates and other information relating to our Services, provide information that you request, respond to comments and questions, and otherwise provide customer support;</li>
            <li>For marketing purposes, such as developing and providing promotional and advertising materials that may be useful, relevant, valuable or otherwise of interest to you;</li>
            <li>To generate deidentified (personally identifiable information is removed) reports for business purposes outlined in this section;</li>
            <li>To send you text messages;</li>
            <li>To facilitate transactions and payments;</li>
            <li>To find and prevent fraud, and respond to trust and safety issues that may arise;</li>
            <li>For compliance purposes, including enforcing our Terms and Conditions or other legal rights, or as may be required by applicable laws and regulations or requested by any judicial process or governmental agency; and</li>
            <li>For other purposes for which we provide specific notice at the time the information is collected.</li>
        </ul>

        <h3>How We Share the Information We Collect</h3>
        <p>We may share or otherwise disclose information we collect from or about you as described below or otherwise disclosed to you at the time of collection.</p>
        <ul class="list list_dot">
            <li><strong>Associated Toll Facility Operators.</strong> We share certain information about you, such as your TAPNPAY customer number, LPN, date of enrollment in our Services, toll payment history, or other third-party account number, and other information related to your use of our Services, with ATFOs in connection with transactions related to our Services and in connection with their internal business purposes.</li>
            <li><strong>Vendors and Service Providers.</strong> Any information you provide to us or that we collect when you use our Services may be shared by us with ATFOs, vendors and service providers (including third parties that support the process for having your toll charges paid) in connection with the provision of our Services, provided that such ATFOs, vendors and service providers may only use such information for the purposes of providing our Services.</li>
            <li><strong>Analytics Partners.</strong> We use analytics services such as Google Analytics to collect and process certain analytics data. These services may also collect information about your use of other websites, apps, and online resources. You can learn about Google's practices by going to <a target="_blank" rel="nofollow noopener" href="https://www.google.com/policies/privacy/partners/">https://www.google.com/policies/privacy/partners/</a>, and opt-out of them by downloading the Google Analytics opt-out browser add-on, available at <a target="_blank" rel="nofollow noopener" href="https://tools.google.com/dlpage/gaoptout">https://tools.google.com/dlpage/gaoptout</a>.</li>
            <li><strong>As Required by Law and Similar Disclosures.</strong> We may access, preserve, and disclose information about you if we believe doing so is required or appropriate to: (a) comply with law enforcement requests and legal process, such as a court order or subpoena; (b) respond to your requests; or (c) protect your, our, or others' rights, property, or safety.</li>
            <li><strong>Merger, Sale, or Other Asset Transfers.</strong> We may disclose or transfer your information to service providers, advisors, potential transactional partners, or other third parties in connection with the consideration, negotiation, or completion of a corporate transaction in which we are acquired by or merged with another company or we sell, liquidate, or transfer all or a portion of our business or assets.</li>
            <li><strong>Consent.</strong> We may also disclose information from or about you or your devices with your permission.</li>
            <li><strong>Your Choices</strong></li>
            <li><strong>Marketing Communications.</strong> You can unsubscribe from our promotional messages via the method provided in the emails and texts. Even if you opt-out of receiving promotional messages from us, you will continue to receive administrative messages from us.</li>
        </ul>

        <h3>Third Parties</h3>
        <p>Our Services may contain links to other websites, products, or services that we do not own or operate. We are not responsible for the privacy practices of these third parties. Please be aware that this Privacy Policy does not apply to your activities on these third-party services or any information you disclose to these third parties. We encourage you to read their privacy policies before providing any information to them.</p>

        <h3>Security</h3>
        <p>We make reasonable efforts to protect your information by using physical and electronic safeguards designed to improve the security of the information we maintain. However, as our Services are hosted electronically, we can make no guarantees as to the security or privacy of your information.</p>

        <h3>Children's Privacy</h3>
        <p>We do not knowingly collect, maintain, or use personal information from children under 13 years of age, and no part of our Services are directed to children. If you learn that a child has provided us with personal information in violation of this Privacy Policy, then you may alert us at <a rel="nofollow noopener" href="mailto:support@tapnpay.com">support@tapnpay.com</a>.</p>

        <h3>International Visitors</h3>
        <p>Our Services are hosted in the United States and intended for visitors located within the United States. If you choose to use our Services from the European Union or other regions of the world with laws governing data collection and use that may differ from U.S. law, then please note that you are transferring your personal information outside of those regions to the United States for storage and processing. Also, we may transfer your data from the U.S. to other countries or regions in connection with storage and processing of data, fulfilling your requests, and operating our Services. By providing any information, including personal information, on or to our Services, you consent to such transfer, storage, and processing.</p>

        <h3>Update Your Information or Pose a Question</h3>
        <p>You can close your account by deregistering your license plate on the tapNpay payment site on the account settings page found here: <a target="_blank" rel="nofollow noopener" href="https://tapnpay.biz/dashboard/profile">https://tapnpay.biz/dashboard/profile</a>. If you have questions about your privacy on our Services or this Privacy Policy, please contact us at <a rel="nofollow noopener" href="mailto:support@tapnpay.com">support@tapnpay.com</a>.</p>

        <h3>Changes to this Privacy Policy</h3>
        <p>We will post any adjustments to the Privacy Policy on this page, and the revised version will be effective when it is posted. If we materially change the ways in which we use or share personal information previously collected from you through our Services, we will attempt to notify you through our Services, by email, or other means.</p>

        <h3>Contact Information</h3>
        <p>If you have any questions, comments, or concerns about our processing activities, please email us at <a rel="nofollow noopener" href="mailto:support@tapnpay.com">support@tapnpay.com</a> or write to us at 1464 E. Whitestone Blvd, Suite 1904, Cedar Park, TX, 78613.</p>

        <p><strong>Last Updated:</strong> December 07, 2021</p>
    </div>
</div>

<!-- /// -->

<?php wp_footer(); ?>

</body>
</html>
