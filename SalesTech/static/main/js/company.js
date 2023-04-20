$(document).ready(function () {
    $('.page-loading').hide();
    $(window).on('hashchange', function () {
        showHideSearchForms();
        $('.pagination').addClass("d-none")
    });
    if (window.location.hash) {
        showHideSearchForms();
    } else if (window.location.href.includes("company/find-clients")) {
        window.location.hash = '#byname'
        showHideSearchForms();
    }
    $("#by_name").submit(function (event) {
        $('.page-loading').show();
    })
    $("#by_domain").submit(function (event) {
        $('.page-loading').show();
    })
    $("#by_feature").submit(function (event) {
        $('.page-loading').show();
    })
    $('#id_company_branch').select2({
        selectionCssClass: "form-select-control",
        width: 'resolve',
        language: {
            noResults: function () {
                return gettext("No results found")
            }
        }
    });
    $('#id_company_size').select2({
        selectionCssClass: "form-select-control",
        width: 'resolve',
        language: {
            noResults: function () {
                return gettext("No results found")
            }
        }
    });
    // $('#id_user_lists').select2({
    //     selectionCssClass: "w-100 form-control form-control-user form-select-control mb-3",
    //     width: '466px',
    //     language: {
    //         noResults: function () {
    //             return gettext("No results found")
    //         }
    //     }
    // });
    // $('#id_user_lists').on('select2:opening select2:closing', function (event) {
    //     setTimeout(function () {
    //         $('.select2-search__field').hide();
    //     }, 10);
    // });

    set_text_editor();
    set_templates_message();

    $('#id_company_size').on('select2:opening select2:closing', function (event) {
        setTimeout(function () {
            $('.select2-search__field').hide();
        }, 10);
    });

    let params = (new URL(document.location)).searchParams;
    set_chosen_list(params);

    //TODO странная функция, нужно будет подумать над ней
    // $('.basicAutoComplete').autoComplete(
    //     {minLength: 1}
    // );
    // $('.dropdown-menu').css({'top': 'auto', 'left': 'auto'})

});


function set_text_editor() {
    $("[id^=txtEditor_]").each(function () {
        $(this).Editor({

            "insert_table": false,

            "print": false,

            "hr_line": false,

            "insert_img": false,

            "select_all": false,

        });
    });
}

$(document).on('click', '[id^=subject_line_variable]', function () {
    let list_id = this.dataset.list_id,
        variable = this.dataset.variable,
        subject_line = $(`#subject_line${list_id}`).val();
    if (subject_line) subject_line += ` {{${variable}}}`;
    else subject_line += `{{${variable}}}`;

    $(`#subject_line${list_id}`).val(subject_line);
});


$(document).on('click', '[id^=edit_subject_line_variable]', function () {
    let template_id = this.dataset.template_id || '',
        variable = this.dataset.variable,
        subject_line = $(`#edit_subject_line${template_id}`).val();
    if (subject_line) subject_line += ` {{${variable}}}`;
    else subject_line += `{{${variable}}}`;

    $(`#edit_subject_line${template_id}`).val(subject_line);
});


function set_templates_message() {
    $("[id^=txtEditor_0]").each(function () {
        let id = this.id.replace('txtEditor_0',''),
            message = $(`#__message_text${id}`).val();

        $(`#txtEditor_0${id}`).Editor("setText", message);  
    });
}


async function editTemplate(e, id, page) {
    e.preventDefault();
    var template_edit_form = document.querySelector(`#rename_template_form${id}`);
    var name_template = document.querySelector(`#name_template${id}`).value;
    var subject_line = document.querySelector(`#edit_subject_line${id}`).value;
    message = $(`#txtEditor_0${id}`).Editor("getText");

    data = await (await fetch(`/ru/company/templates/get_template_data/${id}/?page=${page}/`)).json();

    if (data.name == name_template && data.subject_line == subject_line && data.message == message) {
        $("#template_edit").show();
        setTimeout(function () {
            $("#template_edit").hide();
        }, 10000);
    } else {

        const csrftoken = Cookies.get('csrftoken');
        fetch(`/ru/company/templates/rename_template/${id}/`, {
            method: 'POST',
            body: JSON.stringify({ 'name_template': name_template, 'subject_line': subject_line, 'message': message }),
            headers: { "X-CSRFToken": csrftoken }
        }).then(response => console.log(response));
        template_edit_form.submit();
    }
}


async function settemplatechange(selectObject) {
    var val = selectObject.value;

    data = await (await fetch(`/ru/company/templates/get_template_data/${val}/`)).json();

    $(`#txtEditor_1`).Editor("setText", data['message']);
    document.getElementById('edit_subject_line').value = data['subject_line'];
}

async function settgtemplatechange(selectObject) {
    var val = selectObject.value;

    data = await (await fetch(`/ru/company/templates/get_template_data/${val}/`)).json();

    $(`#tg_msg`).val(data['message']);
    document.getElementById('tg_subject_line').value = data['subject_line'];
}


function showHideSearchForms() {
    $('#collapseTwo').removeClass("show");
    switch (window.location.hash) {
        case '#byname':
            $('.search-for-domain').addClass("d-none");
            $('.search-for-name').removeClass("d-none");
            $('.search-for-feature').addClass("d-none");
            break;
        case '#bydomain':
            $('.search-for-name').addClass("d-none");
            $('.search-for-domain').removeClass("d-none");
            $('.search-for-feature').addClass("d-none");
            break;
        case '#byfeature':
            $('.search-for-name').addClass("d-none");
            $('.search-for-domain').addClass("d-none");
            $('.search-for-feature').removeClass("d-none");
            break;
    }
}


function company_field_changed(value) {
    console.log(`New value in filed is ${value}`)
    let company_url_field = document.getElementById("id_site")
    fetch(`/ru/company/company_info?company_name=${value}`).then(response => response.json())
        .then(result => {
            if (result.url)
                company_url_field.value = result.url
        })
    console.log(result)

}

function remove_clients(list_id, table_id) {
    const datatable = `DataTables_Table_${table_id - 1}`
    const selected_rows = $(`table[id=${datatable}]`).find('tbody').find('.selected')
    const selected_rows_array = [...selected_rows]
    const ids_to_delete = selected_rows_array.map(row => row.getElementsByTagName("td")[0].id)


    const csrftoken = Cookies.get('csrftoken');
    fetch('/ru/company/delete_contact/', {
        method: 'POST',
        body: JSON.stringify({ 'ids_to_delete': ids_to_delete }),
        headers: { "X-CSRFToken": csrftoken }
    })
        // .then(response => response.json()).then(json => console.log(json))
        .then(response => console.log(response))
}

async function ask_for_latinizator() {
    const first_name_field = document.getElementById("firstname")
    const last_name_field = document.getElementById("surname")
    const domain_field = document.getElementById("id_site")

    if (first_name_field.value.length > 0 && last_name_field.value.length > 0 && domain_field.value.length > 0) {
        const email_field = document.getElementById("email")
        let emails
        await fetch(`/ru/company/generate_emails?first_name=${first_name_field.value}&surname=${last_name_field.value}&domain=${domain_field.value}`).then(response => response.json()).then(result => emails = result.emails)
        if (emails.length > 0) {
            email_field.value = emails[0]
        } else {
            $(".myAlert-bottom").show();
            setTimeout(function () {
                $(".myAlert-bottom").hide();
            }, 5000);
        }
    } else {
        if (first_name_field.value.length == 0) {
            first_name_field.placeholder = gettext("Input name!")
        }
        if (last_name_field.value.length == 0) {
            last_name_field.placeholder = gettext("Input surname!")
        }
        if (domain_field.value.length == 0) {
            domain_field.placeholder = gettext("Input domain!")
        }
    }
}


function set_chosen_list(params) {
    let chlist = params.get("chlist");
    if (chlist != null) {
        var chosen_list = document.getElementById(`list-home-list${chlist}`);
        chosen_list.classList.add("active");
        chosen_list.setAttribute('aria-selected', true);

        var tab_pane = document.getElementById(`list${chlist}`);
        tab_pane.classList.add("active");
    }
}


function home_change_page(_page, list_id) {
    let url = new URL(document.location);
    let params = url.searchParams;

    let chlist = params.get("chlist");
    if (chlist != null) {
        params.set('chlist', list_id);
    } else {
        params.append('chlist', list_id);
    }

    let page = params.get("page");
    if (page != null) {
        params.set('page', _page);
    } else {
        params.append('page', _page);
    }

    document.location.replace(url.href)
}


function find_clients_change_page(page) {

    var input = document.createElement("input");
    input.setAttribute('type', 'text');
    input.setAttribute('hidden', true);
    input.setAttribute('value', page);
    input.setAttribute('name', 'page');
    input.setAttribute('id', 'page');

    switch (window.location.hash) {
        case '#byname':
            var form = document.getElementById('by_name');
            break;
        case '#bydomain':
            var form = document.getElementById('by_domain');
            break;
        case '#byfeature':
            var form = document.getElementById('by_feature');
            break;
    }
    form.appendChild(input);
    form.elements['submit'].click()
}


function tgsubjectline_setuserlocalvarable(variable) {
    var tg_subject_line = $('#tg_subject_line').val();
    if (tg_subject_line) tg_subject_line += ` {{${variable}}}`;
    else tg_subject_line += `{{${variable}}}`;

    $('#tg_subject_line').val(tg_subject_line);
}


function tgmsg_setuserlocalvarable(variable) {
    var tg_msg = $('#tg_msg').val();
    if (tg_msg) tg_msg += ` {{${variable}}}`;
    else tg_msg += `{{${variable}}}`;

    $('#tg_msg').val(tg_msg);
}


$(document).on('submit', '#add_contacts_list_form', function(e) {
    e.preventDefault();

    var list_name = $('#list_name').val()
        url = this.dataset.url;

    $('#addUserListModalCenter').modal('hide')

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'POST',
		data: JSON.stringify({
			'list_name': list_name
		}),
		success: function (resposne) {
			document.getElementById(`contacts-lists`).innerHTML = resposne;

            $(`#list_success_created`).show();
            setTimeout(function () {
                $(`#list_success_created`).hide();
            }, 5000);

		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('submit', '[id^=rename_contacts_list_form]', function(e) {
    e.preventDefault();

    var list_id = this.dataset.list_id
        name_list = $(`#name_list${list_id}`).val()
        url = this.dataset.url;

    $(`#rename_list${list_id}`).modal('hide')
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'PATCH',
		data: JSON.stringify({
            'list_id': list_id,
			'name_list': name_list
		}),
		success: function (resposne) {
			document.getElementById(`contacts-lists`).innerHTML = resposne;

            $(`#list_success_edited`).show();
            setTimeout(function () {
                $(`#list_success_edited`).hide();
            }, 5000);

		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('click', '[id^=delete_contacts_list_button]', function(e) {
    e.stopImmediatePropagation();

    var list_id = this.dataset.list_id
        url = this.dataset.url;

    $(`#delete_contacts_list${list_id}`).modal('hide')
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'DELETE',
		data: JSON.stringify({
            'list_id': list_id,
		}),
		success: function (resposne) {
			document.getElementById(`contacts-lists`).innerHTML = resposne;

            $(`#list_success_deleted`).show();
            setTimeout(function () {
                $(`#list_success_deleted`).hide();
            }, 5000);

		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('submit', '[id^=addUserForm_]', function (e) {
    e.preventDefault();

    let url = this.dataset.url,
        list_id = this.dataset.list_id,
        first_name = $('#firstname').val(),
        surname = $('#surname').val(),
        middle_name = $('#middle_name').val(),
        email = $('#email').val(),
        phone_number = $('#id_phone_number').val(),
        position = $('#position').val(),
        company = $('#id_company').val(),
        site = $('#id_site').val(),
        telegram_id = $('#id_telegram_id').val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
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
        success: function (resposne) {
            $(`#addUserModalLong_${list_id}`).modal('hide');
            document.getElementById(`contacts-lists`).innerHTML = resposne;

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


$(document).on('click', '[id^=reedit_contact__button]', function (e) {
    e.preventDefault();

    let url = this.dataset.url,
        contact_id = this.dataset.contact_id,
        first_name = $(`#edit_contact_first_name${contact_id}`).val(),
        surname = $(`#edit_contact_last_name${contact_id}`).val(),
        middle_name = $(`#edit_contact_midname${contact_id}`).val(),
        email = $(`#edit_contact_email${contact_id}`).val(),
        phone_number = $(`#edit_contact_phone${contact_id}`).val(),
        position = $(`#edit_contact_position${contact_id}`).val(),
        company = $(`#edit_contact_company_name${contact_id}`).val(),
        site = $(`#edit_contact_company_site${contact_id}`).val(),
        telegram_id = $(`#edit_contact_telegram_id${contact_id}`).val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            contact_id: contact_id,
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
        success: function (resposne) {
            $(`#editcontactModalCenter${contact_id}`).modal('hide');
            document.getElementById(`contacts-lists`).innerHTML = resposne;

            $('#contact_success_edited').show();
            setTimeout(function () {
                $('#contact_success_edited').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=transfer_contact_button_]', function(e) {
    e.stopImmediatePropagation();

    var container_id = this.dataset.container_id
        url = this.dataset.url
        new_list_id = $('#id_transfer_contact').val();

    $(`#transfer_contact${container_id}`).modal('hide')
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'PATCH',
		data: JSON.stringify({
			container_id: container_id,
            new_list_id: new_list_id
		}),
		success: function (resposne) {

			document.getElementById(`contacts-lists`).innerHTML = resposne;

            $(`#contact_success_transfered`).show();
            setTimeout(function () {
                $(`#contact_success_transfered`).hide();
            }, 5000);

		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('click', '[id^=contact_delete_button]', function(e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        container_id = this.dataset.container_id,
        contact_id = this.dataset.contact_id,
        url = this.dataset.url;

    $(`#delete_contact${contact_id}`).modal('hide')
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'DELETE',
		data: JSON.stringify({
			'container_id': container_id,
            'contact_id': contact_id
		}),
		success: function (resposne) {

			document.getElementById(`contacts-lists`).innerHTML = resposne;

            $(`#delete_contact_success`).show();
            setTimeout(function () {
                $(`#delete_contact_success`).hide();
            }, 5000);

            show_tab_after_ajax(list_id);
		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('submit', '[id^=contacts_search_form]', function(e) {
    e.preventDefault();

    var list_id = this.dataset.list_id
        url = this.dataset.url
        search_name = $(`#search_name${list_id}`).val()
        search_surname = $(`#search_surname${list_id}`).val()
        search_domain = $(`#search_domain${list_id}`).val();

    search_button = $(`#search_form_submit${list_id}`);
    search_button.attr('value', gettext('Search in progress...'));
    search_button.prop('disabled', true);
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'POST',
		data: JSON.stringify({
            'list_id': list_id,
			'search_name': search_name,
            'search_surname': search_surname,
            'search_domain': search_domain
		}),
		success: function (resposne) {
			document.getElementById(`contacts-lists`).innerHTML = resposne;

            if (search_name || search_surname || search_domain) {
                let row_html = $(`#contacts_search_form_row${list_id}`).html(),
                    refresh_button = `<div class="col-sm"><label for="submit"><br></label><button type="submit" class="btn btn-warning btn-user btn-block" id="refresh_search_form${list_id}" data-list_id="${list_id}">${gettext('Reset')}</button></div>`;
                $(`#contacts_search_form_row${list_id}`).html(row_html + refresh_button)
            }

            $(`#search_name${list_id}`).val(search_name);
            $(`#search_surname${list_id}`).val(search_surname);
            $(`#search_domain${list_id}`).val(search_domain);

            search_button.attr('value', gettext('Find contact'));
            search_button.prop('disabled', false);

            $(`#search_contacts_success`).show();
            setTimeout(function () {
                $(`#search_contacts_success`).hide();
            }, 5000);

            show_tab_after_ajax(list_id);
		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('click', '[id^=refresh_search_form]', function () {
    let list_id = this.dataset.list_id;

    $(`#search_name${list_id}`).val('');
    $(`#search_surname${list_id}`).val('');
    $(`#search_domain${list_id}`).val('');
    $(`#contacts_search_form${list_id}`).submit();

})


$(document).on('submit', '[id^=bulk_transfer_contact_form]', function(e) {
    e.preventDefault();

    var list_id = this.dataset.list_id
        trans_list_value = $(`#id_bulk_transfer_contact_${list_id}`).val()
        contact_actions_form = $(`#contact_actions_form${list_id}`);
    
    $(`#bulk_transfer_contact${list_id}`).modal('toggle');
    
    contact_actions_form.data('trans_id', trans_list_value);
    contact_actions_form.submit();   
});


$(document).on('click', '[id^=bulk_delete_button]', function(e) {
    e.preventDefault();

    var list_id = this.dataset.list_id
        contact_actions_form = $(`#contact_actions_form${list_id}`);
    
    $(`#bulk_delete_contact${list_id}`).modal('toggle');
    
    contact_actions_form.data('bulk_del', true);
    contact_actions_form.submit();
});


$(document).on('submit', '[id^=contact_actions_form]', function(e) {
    e.preventDefault();

    let list_id = this.dataset.list_id,
        contact_actions_submit = $(`#contact_actions_submit${list_id}`),
        contact_actions_form = $(`#contact_actions_form${list_id}`),
        trans_id = contact_actions_form.data('trans_id'),
        bulk_del = contact_actions_form.data('bulk_del'),
        url = contact_actions_form.data('update_url'),
        page = contact_actions_form.data('page'),
        actions_value = $(`#actions-${list_id}`).val(),
        checks = [];

    if (!actions_value) {
        $('#bulk_contacts_select_action').show();
        setTimeout(function () {
            $('#bulk_contacts_select_action').hide();
        }, 5000);
        return
    }
    
    
    if (actions_value == 'trans' && !trans_id) {
        $(`#bulk_transfer_contact${list_id}`).modal('show');
        return
    } else if (actions_value == 'del' && !bulk_del) {
        $(`#bulk_delete_contact${list_id}`).modal('show');
        return
    }

    $(`[id^=contact-check-${list_id}-]`).each(function(i, obj) {
        if (obj.checked) checks.push(obj.dataset.container_id)
    });

    if (!checks.length) {
        $('#bulk_contacts_select_contact').show();
        setTimeout(function () {
            $('#bulk_contacts_select_contact').hide();
        }, 5000);
        return
    }

    switch(actions_value) {
        case 'trans':
            contact_actions_submit.html(gettext('Transferring...'))
            break;
        case 'del':
            contact_actions_submit.html(gettext('Removing...'))
            break;
    }
    contact_actions_submit.prop('disabled', true);
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: {"X-CSRFToken": csrftoken},
        contentType: 'application/json; charset=utf-8',
		url: url,
		type: 'POST',
		data: JSON.stringify({
            'list_id': list_id,
			'containers_ids': checks,
            'trans_id': trans_id,
            'action': actions_value,
            'page': page
		}),
		success: function (resposne) {
			document.getElementById(`contacts-lists`).innerHTML = resposne;

            contact_actions_submit.html(gettext('Submit'));
            contact_actions_submit.prop('disabled', false);

            $(`#bulk_contacts_${actions_value}_alert`).show();
            setTimeout(function () {
                $(`#bulk_contacts_${actions_value}_alert`).hide();
            }, 5000);

            show_tab_after_ajax(list_id);
		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
    
});


$(document).on('click', '[id^=contacts-checks-button]', function(e) {
    e.stopImmediatePropagation();

    let check = this.checked,
        list_id = this.dataset.list_id;
    

    $(`[id^=contact-check-${list_id}-]`).each(function(i, obj) {
        if (check) obj.checked = true;
        else obj.checked = false
    });
});


$(document).on('click', '[id^=contacts-paginator]', function (e) {

    let list_id = this.dataset.list_id,
        url = this.dataset.url,
        value = this.dataset.value;

    $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'GET',
        data: {
            page: value,
        },
        success: function (resposne) {
            document.getElementById(`contacts_table${list_id}`).innerHTML = resposne;
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});




$(document).on('submit', '#add_templates_list_form', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_name = $('#id_list_name').val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'list_name': list_name
        }),
        success: function (resposne) {
            $('#addUserListModalCenter').modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;
            
            set_text_editor();
            set_templates_message();

            $('#list_success_created').show();
            setTimeout(function () {
                $('#list_success_created').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '#template_list_edit_form', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id,
        name_list = $(`#name_list${list_id}`).val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            'list_id': list_id,
            'name_list': name_list
        }),
        success: function (resposne) {
            $(`#templateslistrenameModalCenter${list_id}`).modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            $('#list_success_edited').show();
            setTimeout(function () {
                $('#list_success_edited').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '#delete_templates_list', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id;

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'DELETE',
        data: JSON.stringify({
            'list_id': list_id
        }),
        success: function (resposne) {
            $(`#delete_template_list${list_id}`).modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            $('#list_success_deleted').show();
            setTimeout(function () {
                $('#list_success_deleted').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '[id^=addTemplateForm_]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id,
        name_template = $(`#template_name${list_id}`).val(),
        subject_line = $(`#subject_line${list_id}`).val(),
        message = $(`#txtEditor_${list_id}`).Editor("getText");

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'name_template': name_template,
            'subject_line': subject_line,
            'message': message
        }),
        success: function (resposne) {
            $(`#addTemplateLong_${list_id}`).modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            $('#template_success_created').show();
            setTimeout(function () {
                $('#template_success_created').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '[id^=rename_template_form]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        template_id = this.dataset.template_id,
        name_template = $(`#name_template${template_id}`).val(),
        subject_line = $(`#edit_subject_line${template_id}`).val(),
        message = $(`#txtEditor_0${template_id}`).Editor("getText");

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            'template_id': template_id,
            'name_template': name_template,
            'subject_line': subject_line,
            'message': message
        }),
        success: function (resposne) {
            $(`#renametemplateModalCenter${template_id}`).modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            $('#template_success_edited').show();
            setTimeout(function () {
                $('#template_success_edited').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=delete_template_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        template_id = this.dataset.template_id;

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'DELETE',
        data: JSON.stringify({
            'template_id': template_id
        }),
        success: function (resposne) {
            $(`#delete_template${template_id}`).modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            $('#template_success_deleted').show();
            setTimeout(function () {
                $('#template_success_deleted').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=transfer_template_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        template_id = this.dataset.template_id,
        new_list_id = $(`#id_transfer_template${template_id}`).val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            'template_id': template_id,
            'new_list_id': new_list_id
        }),
        success: function (resposne) {
            $(`#transfer_template${template_id}`).modal('hide');
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            $('#template_success_transferred').show();
            setTimeout(function () {
                $('#template_success_transferred').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=bulk_transfer_template_submit_]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        trans_list_value = $(`#id_bulk_transfer_template_${list_id}`).val(),
        actions_submit = $(`#templates-actions_submit-${list_id}`);

    $(`#bulk_transfer_template${list_id}`).modal('toggle');

    actions_submit.data('trans_id', trans_list_value);
    actions_submit.click();
});


$(document).on('click', '[id^=bulk_delete_template_button]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#templates-actions_submit-${list_id}`);

    $(`#bulk_delete_template${list_id}`).modal('toggle');

    actions_submit.data('bulk_del', true);
    actions_submit.click();
});


$(document).on('click', '[id^=templates-actions_submit-]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#templates-actions_submit-${list_id}`),
        bulk_del = actions_submit.data('bulk_del'),
        trans_id = actions_submit.data('trans_id'),
        url = actions_submit.data('update_url'),
        page = actions_submit.data('page'),
        actions_value = $(`#templates-actions-${list_id}`).val(),
        checks = [];

    if (!actions_value) {
        $('#bulk_templates_select_action').show();
        setTimeout(function () {
            $('#bulk_templates_select_action').hide();
        }, 5000);
        return
    }

    if (actions_value == 'del' && !bulk_del) {
        $(`#bulk_delete_template${list_id}`).modal('show');
        return
    } else if (actions_value == 'trans' && !trans_id) {
        $(`#bulk_transfer_template${list_id}`).modal('show');
        return
    }

    $(`[id^=template-check-${list_id}-]`).each(function (i, obj) {
        if (obj.checked) checks.push(obj.dataset.template_id)
    });

    if (!checks.length) {
        $('#bulk_templates_select_template').show();
        setTimeout(function () {
            $('#bulk_templates_select_template').hide();
        }, 5000);
        return
    }

    if (actions_value == 'del') actions_submit.html(gettext('Removing...'))
    else if (actions_value == 'trans') actions_submit.html(gettext('Transferring...'))
    actions_submit.prop('disabled', true);

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'list_id': list_id,
            'trans_id': trans_id,
            'templates': checks,
            'action': actions_value,
            'page': page
        }),
        success: function (resposne) {
            document.getElementById(`templates-list`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();

            actions_submit.html(gettext('Submit'));
            actions_submit.prop('disabled', false);

            $(`#bulk_templates_${actions_value}_alert`).show();
            setTimeout(function () {
                $(`#bulk_templates_${actions_value}_alert`).hide();
            }, 5000);

            show_tab_after_ajax(list_id);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});


$(document).on('click', '[id^=templates-checks_button-]', function (e) {
    e.stopImmediatePropagation();

    let check = this.checked,
        list_id = this.dataset.list_id;

    $(`[id^=template-check-${list_id}-]`).each(function (i, obj) {
        if (check) obj.checked = true;
        else obj.checked = false
    });
});


$(document).on('click', '[id^=template-paginator]', function (e) {

    let list_id = this.dataset.list_id,
        url = this.dataset.url,
        value = this.dataset.value;

    $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'GET',
        data: {
            page: value
        },
        success: function (resposne) {
            document.getElementById(`templates-table${list_id}`).innerHTML = resposne;

            set_text_editor();
            set_templates_message();
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});




$(document).on('submit', '#add_newsletter_list_form', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_name = $('#list_name').val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'list_name': list_name
        }),
        success: function (resposne) {
            $('#addUserListModalCenter').modal('hide');
            document.getElementById(`newsletters-list`).innerHTML = resposne;

            $('#list_success_created').show();
            setTimeout(function () {
                $('#list_success_created').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '[id^=edit_newsletter_list_form]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id,
        name_list = $(`#name_list${list_id}`).val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            'name_list': name_list
        }),
        success: function (resposne) {
            $(`#rename_newsletter_list${list_id}`).modal('hide');
            document.getElementById(`newsletters-list`).innerHTML = resposne;

            $('#list_success_edited').show();
            setTimeout(function () {
                $('#list_success_edited').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '#delete_newsletters_list', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id;

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'DELETE',
        data: JSON.stringify({
            'list_id': list_id
        }),
        success: function (resposne) {
            $(`#delete_newsletters_list${list_id}`).modal('hide');
            document.getElementById(`newsletters-list`).innerHTML = resposne;

            $('#list_success_deleted').show();
            setTimeout(function () {
                $('#list_success_deleted').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=delete_newsletter_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        newsletter_id = this.dataset.newsletter_id;

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'DELETE',
        data: JSON.stringify({
            'newsletter_id': newsletter_id
        }),
        success: function (resposne) {
            $(`#delete_newsletter${newsletter_id}`).modal('hide');
            document.getElementById(`newsletters-list`).innerHTML = resposne;

            $('#delete_newsletter_success').show();
            setTimeout(function () {
                $('#delete_newsletter_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=transfer_newsletter_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        newsletter_id = this.dataset.newsletter_id,
        new_list_id = $(`#id_transfer_newsletter${newsletter_id}`).val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            'newsletter_id': newsletter_id,
            'new_list_id': new_list_id
        }),
        success: function (resposne) {
            $(`#transfer_newsletter${newsletter_id}`).modal('hide');
            document.getElementById(`newsletters-list`).innerHTML = resposne;

            $('#transfer_newsletter_success').show();
            setTimeout(function () {
                $('#transfer_newsletter_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=bulk_transfer_newsletter_submit_]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        trans_list_value = $(`#id_bulk_transfer_newsletter_${list_id}`).val(),
        actions_submit = $(`#newsletters-actions_submit-${list_id}`);

    $(`#bulk_transfer_newsletter${list_id}`).modal('toggle');

    actions_submit.data('trans_id', trans_list_value);
    actions_submit.click();
});


$(document).on('click', '[id^=bulk_delete_newsletter_button]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#newsletters-actions_submit-${list_id}`);

    $(`#bulk_delete_newsletter${list_id}`).modal('toggle');

    actions_submit.data('bulk_del', true);
    actions_submit.click();
});


$(document).on('click', '[id^=newsletters-actions_submit-]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#newsletters-actions_submit-${list_id}`),
        bulk_del = actions_submit.data('bulk_del'),
        trans_id = actions_submit.data('trans_id'),
        url = actions_submit.data('update_url'),
        page = actions_submit.data('page'),
        actions_value = $(`#newsletters-actions-${list_id}`).val(),
        checks = [];

    if (!actions_value) {
        $('#bulk_newsletters_select_action').show();
        setTimeout(function () {
            $('#bulk_newsletters_select_action').hide();
        }, 5000);
        return
    }

    if (actions_value == 'del' && !bulk_del) {
        $(`#bulk_delete_newsletter${list_id}`).modal('show');
        return
    } else if (actions_value == 'trans' && !trans_id) {
        $(`#bulk_transfer_newsletter${list_id}`).modal('show');
        return
    }

    $(`[id^=newsletter-check-${list_id}-]`).each(function (i, obj) {
        if (obj.checked) checks.push(obj.dataset.newsletter_template_id)
    });

    if (!checks.length) {
        $('#bulk_newsletters_select_newsletter').show();
        setTimeout(function () {
            $('#bulk_newsletters_select_newsletter').hide();
        }, 5000);
        return
    }

    if (actions_value == 'del') actions_submit.html(gettext('Removing...'))
    else if (actions_value == 'trans') actions_submit.html(gettext('Transferring...'))
    actions_submit.prop('disabled', true);

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'list_id': list_id,
            'trans_id': trans_id,
            'newsletters': checks,
            'action': actions_value,
            'page': page
        }),
        success: function (resposne) {
            document.getElementById(`newsletters-list`).innerHTML = resposne;

            actions_submit.html(gettext('Submit'));
            actions_submit.prop('disabled', false);

            $(`#bulk_newsletters_${actions_value}_alert`).show();
            setTimeout(function () {
                $(`#bulk_newsletters_${actions_value}_alert`).hide();
            }, 5000);

            show_tab_after_ajax(list_id);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});


$(document).on('click', '[id^=newsletters-checks_button-]', function (e) {
    e.stopImmediatePropagation();

    let check = this.checked,
        list_id = this.dataset.list_id;

    $(`[id^=newsletter-check-${list_id}-]`).each(function (i, obj) {
        if (check) obj.checked = true;
        else obj.checked = false
    });
});


$(document).on('click', '[id^=newsletter-paginator]', function (e) {

    let list_id = this.dataset.list_id,
        url = this.dataset.url,
        value = this.dataset.value;

    $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'GET',
        data: {
            page: value
        },
        success: function (resposne) {
            document.getElementById(`newsletters-table${list_id}`).innerHTML = resposne;
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});





$(document).on('submit', '#create_sending_form', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_name = $('#id_add_list_form_list_name').val(),
        add_list_form_templates = $('#id_add_list_form_templates').val(),
        add_list_form_users_lists = $('#id_add_list_form_users_lists').val();

    submit_maling_list();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'list_name': list_name,
            'add_list_form_templates': add_list_form_templates,
            'add_list_form_users_lists': add_list_form_users_lists,
        }),
        success: function (resposne) {
            $('#addUserListModalCenter').modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $('#list_success_created').show();
            setTimeout(function () {
                $('#list_success_created').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


function submit_maling_list() {
    const btn = document.getElementById("submit_mailing_list_btn")
    const body = document.getElementById("create_sending_form_body")
    let node = '<div class="row d-flex align-items-center justify-content-center"><div class=""><div class="page-loading"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div></div></div></div>'
    body.innerHTML = node + body.innerHTML
    btn.disabled = true
    btn.value = gettext("Loading...")
}


$(document).on('submit', '[id^=sendingmails_list_rename_form]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id,
        name_list = $(`#name_list${list_id}`).val();

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            'name_list': name_list
        }),
        success: function (resposne) {
            $(`#sendingmails_list_rename${list_id}`).modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $('#list_success_edited').show();
            setTimeout(function () {
                $('#list_success_edited').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '#delete_sendings_list', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id;

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'DELETE',
        data: JSON.stringify({
            'list_id': list_id
        }),
        success: function (resposne) {
            $(`#delete_sendings_list${list_id}`).modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $('#list_success_deleted').show();
            setTimeout(function () {
                $('#list_success_deleted').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('submit', '[id^=sendingmails_start_form]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id,
        sending_time_radio = $(`input[name='sending_time_radio${list_id}']:checked`).val(),
        sending_time_input = $(`#sending_time_input${list_id}`).val();
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'sending_time_radio': sending_time_radio,
            'sending_time_input': sending_time_input
        }),
        success: function (resposne) {
            $(`#sendingmails_start_modal${list_id}`).modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne['html'];

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            let message_type = resposne['message_type'];
            $(`#${message_type}_alert_message`).text(resposne['message'])
            $(`#${message_type}_alert`).show();
            setTimeout(function () {
                $(`#${message_type}_alert`).hide();
            }, 5000);
            
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=sendingmails_stop_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        list_id = this.dataset.list_id;
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: {},
        success: function (resposne) {
            $(`#sendingmails_stop_modal${list_id}`).modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $('#break_sendings_success').show();
            setTimeout(function () {
                $('#break_sendings_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=break_sending_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        sending_id = this.dataset.sending_id,
        is_email = this.dataset.is_email;
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'PATCH',
        data: JSON.stringify({
            sending_id: sending_id
        }),
        success: function (resposne) {
            $(`#break_sending${sending_id}${is_email}`).modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $('#break_sending_success').show();
            setTimeout(function () {
                $('#break_sending_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=delete_sending_button]', function (e) {
    e.preventDefault();
    let url = this.dataset.url,
        sending_id = this.dataset.sending_id,
        is_email = this.dataset.is_email;
    
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'DELETE',
        data: JSON.stringify({
            sending_id: sending_id
        }),
        success: function (resposne) {
            $(`#delete_sending${sending_id}${is_email}`).modal('hide');
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $('#delete_sending_success').show();
            setTimeout(function () {
                $('#delete_sending_success').hide();
            }, 5000);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });
});


$(document).on('click', '[id^=bulk_sending_break_button]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#sending-actions_submit-${list_id}`);

    $(`#bulk_break_sending${list_id}`).modal('toggle');

    actions_submit.data('bulk_break', true);
    actions_submit.click();
});


$(document).on('click', '[id^=bulk_sending_delete_button]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#sending-actions_submit-${list_id}`);;

    $(`#bulk_delete_sending${list_id}`).modal('toggle');

    actions_submit.data('bulk_del', true);
    actions_submit.click();
});


$(document).on('click', '[id^=sending-actions_submit-]', function (e) {
    e.stopImmediatePropagation();

    let list_id = this.dataset.list_id,
        actions_submit = $(`#sending-actions_submit-${list_id}`),
        bulk_del = actions_submit.data('bulk_del'),
        bulk_break = actions_submit.data('bulk_break'),
        url = actions_submit.data('update_url'),
        page = actions_submit.data('page'),
        actions_value = $(`#sending-actions-${list_id}`).val(),
        emails = [],
        telegrams = [];

    if (!actions_value) {
        $('#bulk_sending_select_contact').show();
        setTimeout(function () {
            $('#bulk_sending_select_contact').hide();
        }, 5000);
        return
    }

    if (actions_value == 'del' && !bulk_del) {
        $(`#bulk_delete_sending${list_id}`).modal('show');
        return
    } else if (actions_value == 'break' && !bulk_break) {
        $(`#bulk_break_sending${list_id}`).modal('show');
        return
    }

    $(`[id^=sending-check-${list_id}-]`).each(function (i, obj) {
        if (obj.checked) {
            if (obj.dataset.is_email == 'True') emails.push(obj.dataset.sending_mail_id)
            else if (obj.dataset.is_email == 'False') telegrams.push(obj.dataset.sending_mail_id)
        }
    });

    if (!emails.length && !telegrams.length) {
        $('#bulk_sending_select_sending').show();
        setTimeout(function () {
            $('#bulk_sending_select_sending').hide();
        }, 5000);
        return
    }

    if (actions_value == 'del') actions_submit.html(gettext('Removing...'))
    else if (actions_value == 'break') actions_submit.html(gettext('Breaking...'))
    actions_submit.prop('disabled', true);

    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'list_id': list_id,
            'emails': emails,
            'telegrams': telegrams,
            'action': actions_value,
            'page': page
        }),
        success: function (resposne) {
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            actions_submit.html(gettext('Submit'));
            actions_submit.prop('disabled', false);

            $(`#bulk_contacts_${actions_value}_alert`).show();
            setTimeout(function () {
                $(`#bulk_contacts_${actions_value}_alert`).hide();
            }, 5000);

            show_tab_after_ajax(list_id);
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});

$(document).on('click', '[id^=sending-checks_button-]', function (e) {
    e.stopImmediatePropagation();

    let check = this.checked,
        list_id = this.dataset.list_id;

    $(`[id^=sending-check-${list_id}-]`).each(function (i, obj) {
        if (check) obj.checked = true;
        else obj.checked = false
    });
});


$(document).on('click', '[id^=start_later_radio]', function (e) {
    $('.sending_time_block').removeClass('d-none');
    $('.sending_time_input').attr('required', true);
});

$(document).on('click', '[id^=start_now_radio]', function (e) {
    $('.sending_time_block').addClass('d-none');
    $('.sending_time_input').attr('required', false);
});


$(document).on('click', '[id^=sending_refresh_button]', function (e) {

    let page = this.dataset.page,
        url = this.dataset.url;

    $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'GET',
        data: {
            'page': page
        },
        success: function (resposne) {
            document.getElementById(`sending_mails-list`).innerHTML = resposne;

            $('[id^=refresh_bar_chart]').each(function (i, button) {
                button.click()
            });

            $(`#success_refresh`).show();
            setTimeout(function () {
                $(`#success_refresh`).hide();
            }, 5000);

        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});


$(document).on('click', '[id^=sending-statuses-]', function (e) {

    let list_id = this.dataset.list_id,
        page = this.dataset.page,
        url = this.dataset.url,
        statuses = [];

    $(`[id^=sending-statuses-${list_id}]`).each(function (i, button) {
        if (button.checked) statuses.push(button.dataset.id)
    });

    $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'GET',
        data: {
            page: page,
            statuses: statuses
        },
        success: function (resposne) {
            document.getElementById(`sendings-table${list_id}`).innerHTML = resposne;

            $(`#success_refresh`).show();
            setTimeout(function () {
                $(`#success_refresh`).hide();
            }, 2500);

        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});


$(document).on('click', '[id^=sending-paginator]', function (e) {

    let list_id = this.dataset.list_id,
        url = this.dataset.url,
        value = this.dataset.value,
        statuses = [];

    $(`[id^=sending-statuses-${list_id}]`).each(function (i, button) {
        if (button.checked) statuses.push(button.dataset.id)
    });

    $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: url,
        type: 'GET',
        data: {
            page: value,
            statuses: statuses
        },
        success: function (resposne) {
            document.getElementById(`sendings-table${list_id}`).innerHTML = resposne;
        },
        error: function (xhr) {
            alert("something wrong!");
        }
    });

});


