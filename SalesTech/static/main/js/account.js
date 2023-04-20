$(document).ready(function () {
    $('#different_email').on('click', function () {
        if ($(this).is(':checked')) {
            $('#imap_credentials').removeClass('d-none');
        } else {
            $('#imap_credentials').addClass('d-none');
        }
    });

    $('#id_local_timezone').select2({
        selectionCssClass: "form-select-control",
        width: 'resolve',
        language: {
            noResults: function () {
                return gettext("No results found")
            }
        }
    });

});

function change_rate_plan(rate_plan_id) {

    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: '/ru/users/change_rate_plan/',
        type: 'POST',
        data: {
            rate_plan_id: rate_plan_id
        },
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            location.reload();
        }

    }).done(function (data) {
        console.log(data);
    });
}

function unsubscribe(company_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: '/ru/users/unsubscribe/',
        type: 'POST',
        data: {
            company_id: company_id
        },
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            location.reload();
        }

    }).done(function (data) {
        console.log(data);
    });
}

async function set_ssl_smtp() {
    const smtp_port = document.getElementById("smtp_port")
    smtp_port.value = 465
}

async function set_tls_smtp() {
    const smtp_port = document.getElementById("smtp_port")
    smtp_port.value = 587
}

async function set_none_smtp() {
    const smtp_port = document.getElementById("smtp_port")
    smtp_port.value = 25
}

async function set_ssl_imap() {
    const smtp_port = document.getElementById("imap_port")
    smtp_port.value = 993
}

async function set_tls_imap() {
    const smtp_port = document.getElementById("imap_port")
    smtp_port.value = 993
}

async function set_none_imap() {
    const smtp_port = document.getElementById("imap_port")
    smtp_port.value = 143
}

async function set_random_delay() {
    const fixed_delay_between_messages = document.getElementById("fixed_delay_between_messages")
    const random_delay_between_messages_from = document.getElementById("random_delay_between_messages_from")
    const random_delay_between_messages_to = document.getElementById("random_delay_between_messages_to")

    fixed_delay_between_messages.value = "";
    random_delay_between_messages_from.value = 5;
    random_delay_between_messages_to.value = 35;

    fixed_delay_between_messages.required = false;
    random_delay_between_messages_from.required = true;
    random_delay_between_messages_from.required = true;


}

async function set_fixed_delay() {
    const fixed_delay_between_messages = document.getElementById("fixed_delay_between_messages")
    const random_delay_between_messages_from = document.getElementById("random_delay_between_messages_from")
    const random_delay_between_messages_to = document.getElementById("random_delay_between_messages_to")

    fixed_delay_between_messages.value = 5;
    random_delay_between_messages_from.value = "";
    random_delay_between_messages_to.value = "";

    fixed_delay_between_messages.required = true;
    random_delay_between_messages_from.required = false;
    random_delay_between_messages_from.required = false;
}


$(document).on('change', '#id_local_timezone', function(e) {
    e.stopImmediatePropagation();
    
    var timezone = this.value
        select = $(this)
        option = select.find(":selected");

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
		url: '/ru/users/timezone/set/',
		type: 'POST',
		data: {
            timezone: timezone
		},
		success: function (resposne) {
            if (resposne['success']) {
                $(`#success_change_timezone`).show();
                setTimeout(function () {
                    $(`#success_change_timezone`).hide();
                }, 5000);
                return
            }
            $(`#error`).show();
            setTimeout(function () {
                $(`#error`).hide();
            }, 5000);

		},
		error: function (xhr) {
		}
	});
    
});