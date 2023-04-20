$(document).ready(function () {
    $('.page-loading').hide();
    $(window).on('hashchange', function () {
        showHideOperatorForms();
    });
    if (window.location.hash) {
        showHideOperatorForms();
    } else if (window.location.href.includes("company/operator_page")) {
        window.location.hash = '#contacts'
        showHideOperatorForms();
    }
    $("#contacts_table").submit(function (event) {
        $('.page-loading').show();
    })
    $("#companies_table").submit(function (event) {
        $('.page-loading').show();
    })
});


function showHideOperatorForms() {
    $('#collapseTwoperator').removeClass("show");
    switch (window.location.hash) {
        case '#contacts':
            $('.companies_paginator').addClass("d-none")
            $('.contacts_paginator').removeClass("d-none")

            $('.search-for-companies').addClass("d-none");
            $('.search-for-contacts').removeClass("d-none");
            $('#contacts_table').show();
            $('#companies_table').hide();
            break;
        case '#companies':
            $('.companies_paginator').removeClass("d-none")
            $('.contacts_paginator').addClass("d-none")

            $('.search-for-contacts').addClass("d-none");
            $('.search-for-companies').removeClass("d-none");
            $('#contacts_table').hide();
            $('#companies_table').show();
            break;
    }
}


function processModalForm() {
    setTimeout(function () {
        if (!$('.modal.fade.show').find('#email_latinization').length) {
            $('.modal.fade.show').find('label[for=email]').addClass('w-100')
            $('.modal.fade.show').find('#email').addClass('d-inline-block w-60')
            $('.modal.fade.show').find('#email').after($("<a class='btn btn-primary ml-3' id='email_latinization' onclick='ask_for_latinizator()'></a>"));
            $('.modal.fade.show').find('#email_latinization').text(gettext('Generate email'))
        }
    }, 200);
}


function show_tab_after_ajax(list_id) {
    var list = document.getElementById(`list-home-list${list_id}`);
    list.classList.add("active");
    list.setAttribute('aria-selected', true);
    var tab_pane = document.getElementById(`list${list_id}`);
    tab_pane.classList.add("active");
}