async function contact_select_change(select) {

    var contact_fields = document.getElementById('contact_fields');

    var contact_id = select.value;
    if (!contact_id) {
        contact_fields.hidden = true;
        document.getElementById('contact_email').value = null
        document.getElementById('contact_phone').value = null
        document.getElementById('company_name').value = null
        document.getElementById('company_site').value = null
        return
    }

    contact_fields.hidden = false;
    data = await (await fetch(`/ru/company/company/get_contact_data/${contact_id}/`)).json();

    if (!(data.company_name && data.company_site)) {
        document.getElementById('company_name').value = gettext('Company not found');
        document.getElementById('company_site').value = gettext('Company not found');
    } else {
        document.getElementById('company_name').value = data.company_name || ''
        document.getElementById('company_site').value = data.company_site || ''
    }

    document.getElementById('contact_email').value = data.email || ''
    document.getElementById('contact_phone').value = data.phone || ''


}

function change_contracts_team_member(url) {
    var team_member_id = $("#team_members").val();

    $.ajax({
        url: url,
        type: 'GET',
        data: {
            team_member_id: team_member_id,
        },
        success: function (resposne) {
            document.getElementById("statuses-block").innerHTML = resposne;
        }
    });
}


function add_contact_fromcontract() {
    $('#new_contract').modal('hide');
}


function add_contact_fromcontract_submit(e, url) {
    e.preventDefault();
    var data = $("#addUserForm").serializeArray();
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: function (data) {
            $('#new_contact').modal('hide');
            var contact_fields = document.getElementById('contact_fields');

            var id = data['id'];
            var full_name = data['full_name'];
            var email = data['email'];
            var phone = data['phone'];
            var company_name = data['company_name'];
            var company_site = data['company_site'];

            var select_contact = document.getElementById("contact");
            var option = document.createElement("option");
            option.text = full_name;
            option.value = id;
            select_contact.add(option);

            option.setAttribute("selected", "selected");

            document.getElementById("contact_email").value = email;
            document.getElementById("contact_phone").value = phone;
            document.getElementById("company_name").value = company_name;
            document.getElementById("company_site").value = company_site;

            contact_fields.hidden = false;
            $('#addUserForm').trigger("reset");
            $('#new_contract').modal('show');
        }
    });
}


async function contract_contact_select_change(select, url, contract_id) {

    var contact_id = select.value;

    $.ajax({
        type: 'GET',
        url: url,
        data: {contract_id: contract_id, contact_id: contact_id},
        success: function (data) {

            var email = data['email'];
            var phone = data['phone'];
            var company_name = data['company_name'];
            var company_site = data['company_site'];

            if (!(data.company_name && data.company_site)) {
                document.getElementById('company_name').value = gettext('Company not found');
                document.getElementById('company_site').value = gettext('Company not found');
            } else {
                document.getElementById('company_name').value = company_name || ''
                document.getElementById('company_site').value = company_site || ''
            }

            document.getElementById('contact_email').value = email || ''
            document.getElementById('contact_phone').value = phone || ''
        }
    });
}

function delete_contract_attachment(contract_id, attachment_number) {
    const csrftoken = Cookies.get('csrftoken')
    $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            type: 'POST',
            url: `/ru/crm/contract/delete_attachment/${contract_id}/`,
            data: {attachment_number: attachment_number},
        }
    )
    window.location.reload()

}