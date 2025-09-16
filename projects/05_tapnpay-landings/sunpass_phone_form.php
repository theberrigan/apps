<div class="phone-form <?php echo $phoneFormStyleClass; ?>">
    <div class="phone-form__message"></div>
    <form class="phone-form__form" method="POST" action="/">
        <fieldset class="phone-form__fieldset">
            <input type="tel" name="phone" class="phone-form__input" placeholder="Enter Cell Phone Number" required>
            <button type="submit" class="phone-form__button" disabled>
                <span class="phone-form__button-caption">Get Started</span>
                <span class="phone-form__button-spinner">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28">
                        <path d="M14,27A13,13,0,1,1,27,14,13.0144,13.0144,0,0,1,14,27ZM14,3A11,11,0,1,0,25,14,11.0125,11.0125,0,0,0,14,3Z" style="fill: currentColor; opacity: 0.2;"></path>
                        <path d="M6.52,24.6333A13.0008,13.0008,0,0,1,14,1V3A11.0007,11.0007,0,0,0,7.6719,22.9985Z" style="fill: currentColor;"></path>
                    </svg>
                </span>
            </button>
        </fieldset>
    </form>
</div>