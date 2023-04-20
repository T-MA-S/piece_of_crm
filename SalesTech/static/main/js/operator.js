$(document).ready(function () {
    $('#id_industry').select2({
        selectionCssClass: "form-select-control",
        width: 'resolve',
        language: {
            noResults: function () {
                return gettext("No results found")
            }
        }
    });
    $('#id_company_edit_branch').select2({
        selectionCssClass: "form-select-control mb-3",
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
    $('#id_company_size').on('select2:opening select2:closing', function (event) {
        setTimeout(function () {
            $('.select2-search__field').hide();
        }, 10);
    });

    $('#id_company_edit_size').select2({
        selectionCssClass: "form-select-control",
        width: 'resolve',
        language: {
            noResults: function () {
                return gettext("No results found")
            }
        }
    });
    $('#id_company_edit_size').on('select2:opening select2:closing', function (event) {
        setTimeout(function () {
            $('.select2-search__field').hide();
        }, 10);
    });

});


function operator_change_page(_page) {
    let url = new URL(document.location);
    let params = url.searchParams;

    let page = params.get("page");
    if (page != null) {
        params.set('page', _page);
    } else {
        params.append('page', _page);
    }

    document.location.replace(url.href)
}


function edit_company_form_submit(form, e, company_id, old_branch, old_size) {
    e.preventDefault();


    var new_branch = document.getElementById(`edit_company${company_id}`).company_branch.value;
    var new_size = document.getElementById(`edit_company${company_id}`).company_size.value;


    if (!((new_branch != old_branch) || (new_size != old_size))) {

        $.ajax({
            data: $(form).serialize(),
            type: $(form).attr('method'),
            url: `/ru/company/get_company_data/${company_id}/`,
            success: function (response) {
                $(".myAlert-bottom").show();
                setTimeout(function () {
                    $(".myAlert-bottom").hide();
                }, 5000);
                
                $(`#edit_company_${company_id}`).modal('toggle');

            },

            error: function (response) {

                alert("Error");

            }
        });
        return false;
    }
    else{
        form.submit();
    }
}