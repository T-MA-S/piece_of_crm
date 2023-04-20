function search_creadits_down() {
    let count = $('#credits_navbar').html();
    $('#credits_navbar').html(count - 1)
}

$(document).on('submit', '#search_by_name_form', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        name = $('#id_name').val(),
        surname = $('#id_surname').val(),
        domain = $('#id_domain').val();
    
    $('.page-loading').show();
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            name: name,
            surname: surname,
            domain: domain
        }),
        success: function (resposne) {
            $('#search-for-name').html(resposne);
            search_creadits_down()

            $('.page-loading').hide();

            $('#search_success').show();
            setTimeout(function () {
                $('#search_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '#search_by_domain_form', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        domain = $('#domain_company').val();
    
    $('.page-loading').show();
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            domain: domain
        }),
        success: function (resposne) {
            $('#search-for-domain').html(resposne);

            $('.page-loading').hide();

            $('#search_success').show();
            setTimeout(function () {
                $('#search_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '#bydomain-paginator', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        domain = this.dataset.domain;
    
    $('.page-loading').show();
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            domain: domain
        }),
        success: function (resposne) {
            $('#search-for-domain').html(resposne);

            $('.page-loading').hide();

            $('#search_success').show();
            setTimeout(function () {
                $('#search_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=unlock_email]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        contact_id = this.dataset.contact_id,
        counter = this.dataset.counter
        by = this.dataset.by;
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            contact_id: contact_id
        }),
        success: function (data) {
            search_creadits_down();
            $(`#contact_email${contact_id}${by}`).text(data.email);
            $(`#unlock_email${counter}`).prop('disabled', true);
            $(`#add_to_list${counter}${by}`).prop('disabled', false);
            $(`#email${counter}${by}`).val(data.email);
            $(`#add_to_list_feauture${contact_id}`).prop('disabled', false);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '[id^=add_user_from_search_form]', function (e) {
    e.preventDefault();
    let index = this.dataset.index,
        by = this.dataset.by,
        list_id = $(`#id_user_lists${index}${by}`).val(),
        first_name = $(`#firstname${index}${by}`).val(),
        surname = $(`#surname${index}${by}`).val(),
        middle_name = $(`#middle_name${index}${by}`).val(),
        email = $(`#email${index}${by}`).val(),
        phone_number = $(`#id_phone_number${index}${by}`).val(),
        position = $(`#position${index}${by}`).val(),
        company = $(`#id_company${index}${by}`).val(),
        site = $(`#id_site${index}${by}`).val(),
        telegram_id = $(`#id_telegram_id${index}${by}`).val();
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: `/ru/company/${list_id}/contacts/create/`,
        type: 'POST',
        data: JSON.stringify({
            first_name: first_name,
            surname: surname,
            middle_name: middle_name,
            email: email,
            phone_number: phone_number,
            position: position,
            company: company,
            site: site,
            telegram_id: telegram_id
        }),
        success: function (data) {
            $(`#add_generated_contact_to_list${index}${by}`).modal('hide');
            $(`#add_to_list${index}${by}`).prop('disabled', true);

            $('#contact_success_created').show();
            setTimeout(function () {
                $('#contact_success_created').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});