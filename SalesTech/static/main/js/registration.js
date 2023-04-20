$('#id_name, #id_phone_number, #id_email, #password_1, #password_2').on('keyup', function () {
    var name = $('#id_name')
    var phone_number = $('#id_phone_number')
    var email = $('#id_email')
    var password_1 = $('#password_1')
    var password_2 = $('#password_2')
    var button = $("#register-button")

    button.attr("disabled", true);

    var success = true;
    if (name.val() == '') {
        name.removeClass('is-valid');
        name.addClass('is-invalid');
        success = false;
    } else {
        name.removeClass('is-invalid');
        name.addClass('is-valid');
    }

    if (phone_number.val() == '') {
        phone_number.removeClass('is-valid');
        phone_number.addClass('is-invalid');
        success = false;
    } else {
        phone_number.removeClass('is-invalid');
    }
    // if (phone_number.val().length < 18) {
    //     phone_number.removeClass('is-valid');
    //     phone_number.addClass('is-invalid');
    // } else {
    //     phone_number.removeClass('is-invalid');
    //     phone_number.addClass('is-valid');
    // }

    if (email.val() == '' || !(email.val().match(/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/))) {
        email.removeClass('is-valid');
        email.addClass('is-invalid');
        success = false;
    } else {
        email.removeClass('is-invalid');
        email.addClass('is-valid');
    }

    if (password_1.val().length < 8 || password_2.val().length < 8 || password_1.val() != password_2.val()) {
        password_1.removeClass('is-valid');
        password_2.removeClass('is-valid');

        password_1.addClass('is-invalid');
        password_2.addClass('is-invalid');
        success = false;
    } else {
        password_1.removeClass('is-invalid');
        password_2.removeClass('is-invalid');

        password_1.addClass('is-valid');
        password_2.addClass('is-valid');
    }

    if (success) button.attr("disabled", false);
})


$('#login_email, #login_password').on('keyup', function () {
    var login_email = $('#login_email');
    var login_password = $('#login_password');
    var button = $('#login_button');

    button.attr("disabled", true);

    var success = true;
    if (login_email.val() == '' || !(login_email.val().match(/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/))) {
        login_email.removeClass('is-valid');
        login_email.addClass('is-invalid');
        success = false;
    } else {
        login_email.removeClass('is-invalid');
        login_email.addClass('is-valid');
    }
    if (login_password.val().length < 8) {
        login_password.removeClass('is-valid');
        login_password.addClass('is-invalid');
        success = false;
    } else {
        login_password.removeClass('is-invalid');
        login_password.addClass('is-valid');
    }

    if (success) button.attr("disabled", false);
})


$('#forgot_email').on('keyup', function () {
    var forgot_email = $('#forgot_email');
    var button = $('#forgot_button');

    button.attr("disabled", true);

    var success = true;
    if (forgot_email.val() == '' || !(forgot_email.val().match(/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/))) {
        forgot_email.removeClass('is-valid');
        forgot_email.addClass('is-invalid');
        success = false;
    } else {
        forgot_email.removeClass('is-invalid');
        forgot_email.addClass('is-valid');
    }
    if (success) button.attr("disabled", false);
})

$('#restore_password_1, #restore_password_2').on('keyup', function () {
    var password_1 = $('#restore_password_1')
    var password_2 = $('#restore_password_2')
    var button = $("#restore_button")

    button.attr("disabled", true);

    var success = true;

    if (password_1.val().length < 8 || password_2.val().length < 8 || password_1.val() != password_2.val()) {
        password_1.removeClass('is-valid');
        password_2.removeClass('is-valid');

        password_1.addClass('is-invalid');
        password_2.addClass('is-invalid');
        success = false;
    } else {
        password_1.removeClass('is-invalid');
        password_2.removeClass('is-invalid');

        password_1.addClass('is-valid');
        password_2.addClass('is-valid');
    }

    if (success) button.attr("disabled", false);
})
