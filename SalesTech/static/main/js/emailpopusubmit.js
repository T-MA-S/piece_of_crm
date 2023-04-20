function setdraganddropjson(draganddropjson, button, kwargs) {

    var data_id = button.getAttribute('data-template-id');
    var before_data_id = button.getAttribute('before-data-id');

    draganddropjson_for_datafun(data_id, kwargs);

    if (Object.values(draganddropjson).length != 0) {
        var keys = [];
        for (let [key, value] of Object.entries(draganddropjson)) { keys.push(Object.keys(value)[0]); }
        if (keys.includes(data_id)) {
            for (let [key, value] of Object.entries(draganddropjson)) {
                for (let [k, v] of Object.entries(value)) {
                    if (data_id == k) {
                        if ('edit_subject_line' in kwargs) {
                            if (kwargs.edit_subject_line != v.edit_subject_line) v.edit_subject_line = kwargs.edit_subject_line
                            if (kwargs.msg_text != v.msg_text) v.msg_text = kwargs.msg_text
                            if ('template_id' in kwargs && kwargs.template_id != null && kwargs.template_id != v.template_id) v.template_id = kwargs.template_id
                            if (!('template_name' in v) && !('template_id' in v)) {
                                if (kwargs.template == null) document.getElementById("addTemplateNButton").click();
                            }
                        } else if ('tg_subject_line' in kwargs) {
                            if (kwargs.tg_subject_line != v.tg_subject_line) v.tg_subject_line = kwargs.tg_subject_line
                            if (kwargs.tg_msg != v.tg_msg) v.tg_msg = kwargs.tg_msg
                            if ('tg_template_id' in kwargs && kwargs.tg_template_id != null && kwargs.tg_template_id != v.tg_template_id) v.tg_template_id = kwargs.tg_template_id
                            if (!('tg_template_name' in v) && !('tg_template_id' in v)) {
                                if (kwargs.template == null) document.getElementById("addTgTemplateNButton").click();
                            }
                        } else if ('delay' in kwargs) {
                            if (kwargs.delay != v.delay) v.delay = kwargs.delay
                        } else if ('goal' in kwargs) {
                            if (kwargs.goal != v.goal) v.goal = kwargs.goal
                        } else if ('template_name' in kwargs) {
                            // console.log(data_id)
                            v.template_name = kwargs.template_name
                        } else if ('tg_template_name' in kwargs) {
                            v.tg_template_name = kwargs.tg_template_name
                        } else if ('trigger' in kwargs) {
                            if (kwargs.trigger != v.trigger) v.trigger = kwargs.trigger
                            if (kwargs.trigger_time != v.trigger_time) v.trigger_time = kwargs.trigger_time
                            if (kwargs.read_unread != v.read_unread) v.read_unread = kwargs.read_unread
                        }
                    }
                }
            }
        } else {
            var trigger_result = false;
            for (let [key, value] of Object.entries(draganddropjson)) {
                for (let [k, v] of Object.entries(value)) {
                    if (Object.keys(v).includes('trigger')) {
                        trigger_result = true;
                        var trigger_key = button.getAttribute('data-loc')
                        var yes_keys = [];
                        for (let [yes_key, yes_value] of Object.entries(v['yes'])) { yes_keys.push(Object.keys(yes_value)[0]); }
                        var no_keys = [];
                        for (let [no_key, no_value] of Object.entries(v['no'])) { no_keys.push(Object.keys(no_value)[0]); }

                        if (k == before_data_id) {
                            settriggerdraganddropjson(v, button, kwargs, trigger_key)
                        } else if (yes_keys.includes(before_data_id)) {
                            settriggerdraganddropjson(v, button, kwargs, 'yes')
                        } else if (no_keys.includes(before_data_id)) {
                            settriggerdraganddropjson(v, button, kwargs, 'no')
                        }
                    }
                }
            }
            if (!trigger_result) {
                if ('edit_subject_line' in kwargs) {
                    if (kwargs.template_id == null) {
                        if (kwargs.edit_subject_line != '' && kwargs.msg_text != '') document.getElementById("addTemplateNButton").click();
                        draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text } });
                    } else {
                        draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text, 'template_id': kwargs.template_id } });
                    }
                }
                else if ('tg_subject_line' in kwargs) {
                    if (kwargs.tg_template_id == null) {
                        if (kwargs.tg_subject_line != '' && kwargs.tg_msg != '') document.getElementById("addTemplateNButton").click();
                        draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg } });
                    } else {
                        draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg, 'tg_template_id': kwargs.template_id } });
                    }
                }
                else if ('delay' in kwargs) draganddropjson.push({ [data_id]: { 'delay': kwargs.delay } })
                else if ('goal' in kwargs) draganddropjson.push({ [data_id]: { 'goal': kwargs.goal } })
                else if ('trigger' in kwargs) draganddropjson.push({ [data_id]: { 'trigger': kwargs.trigger, 'trigger_time': kwargs.trigger_time, 'read_unread': kwargs.read_unread, 'yes': [], 'no': [] } })
            }
        }
    } else {
        if ('edit_subject_line' in kwargs) {
            if (kwargs.template_id == null) {
                if (kwargs.edit_subject_line != '' && kwargs.msg_text != '') document.getElementById("addTemplateNButton").click();
                draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text } });
            } else {
                draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text, 'template_id': kwargs.template_id } });
            }
        }
        else if ('tg_subject_line' in kwargs) {
            if (kwargs.tg_template_id == null) {
                if (kwargs.tg_subject_line != '' && kwargs.tg_msg != '') document.getElementById("addTemplateNButton").click();
                draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg } });
            } else {
                draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg, 'tg_template_id': kwargs.tg_template_id } });
            }
        }
        else if ('delay' in kwargs) draganddropjson.push({ [data_id]: { 'delay': kwargs.delay } })
        else if ('goal' in kwargs) draganddropjson.push({ [data_id]: { 'goal': kwargs.goal } })
        else if ('trigger' in kwargs) draganddropjson.push({ [data_id]: { 'trigger': kwargs.trigger, 'trigger_time': kwargs.trigger_time, 'read_unread': kwargs.read_unread, 'yes': [], 'no': [] } })
    }
    return draganddropjson;
}


function settriggerdraganddropjson(v, button, kwargs, key) {
    if (key == 'yes') setdraganddropjson(v['yes'], button, kwargs)
    else setdraganddropjson(v['no'], button, kwargs)
}

function draganddropjson_for_datafun(data_id, kwargs) {
    var draganddropjson = JSON.parse(document.getElementById('draganddropjson_for_data').value);
    if (Object.values(draganddropjson).length != 0) {
        var keys = [];
        for (let [key, value] of Object.entries(draganddropjson)) { keys.push(Object.keys(value)[0]); }
        if (keys.includes(data_id)) {
            for (let [key, value] of Object.entries(draganddropjson)) {
                for (let [k, v] of Object.entries(value)) {
                    if (data_id == k) {
                        if ('edit_subject_line' in kwargs) {
                            if (kwargs.edit_subject_line != v.edit_subject_line) v.edit_subject_line = kwargs.edit_subject_line
                            if (kwargs.msg_text != v.msg_text) v.msg_text = kwargs.msg_text
                            if (kwargs.template_id != v.template_id) v.template_id = kwargs.template_id
                        } else if ('tg_subject_line' in kwargs) {
                            if (kwargs.tg_subject_line != v.tg_subject_line) v.tg_subject_line = kwargs.tg_subject_line
                            if (kwargs.tg_msg != v.tg_msg) v.tg_msg = kwargs.tg_msg
                            if (kwargs.tg_template_id != v.tg_template_id) v.tg_template_id = kwargs.tg_template_id
                        } else if ('delay' in kwargs) {
                            if (kwargs.delay != v.delay) v.delay = kwargs.delay
                        } else if ('goal' in kwargs) {
                            if (kwargs.goal != v.goal) v.goal = kwargs.goal
                        } else if ('template_name' in kwargs) {
                            v.template_name = kwargs.template_name
                        } else if ('trigger' in kwargs) {
                            if (kwargs.trigger != v.trigger) v.trigger = kwargs.trigger
                            if (kwargs.trigger_time != v.trigger_time) v.trigger_time = kwargs.trigger_time
                            if (kwargs.read_unread != v.read_unread) v.read_unread = kwargs.read_unread
                        }
                    }
                };
            }
        } else {
            if ('edit_subject_line' in kwargs) {
                if (kwargs.template_id == null) {
                    draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text } });
                } else {
                    draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text, 'template_id': kwargs.template_id } });
                }
            }
            else if ('tg_subject_line' in kwargs) {
                if (kwargs.tg_template_id == null) {
                    draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg } });
                } else {
                    draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg, 'tg_template_id': kwargs.tg_template_id } });
                }
            }
            else if ('delay' in kwargs) draganddropjson.push({ [data_id]: { 'delay': kwargs.delay } })
            else if ('goal' in kwargs) draganddropjson.push({ [data_id]: { 'goal': kwargs.goal } })
            else if ('trigger' in kwargs) draganddropjson.push({ [data_id]: { 'trigger': kwargs.trigger, 'trigger_time': kwargs.trigger_time, 'read_unread': kwargs.read_unread } })
        }
    } else {
        if ('edit_subject_line' in kwargs) {
            if (kwargs.template_id == null) {
                draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text } });
            } else {
                draganddropjson.push({ [data_id]: { 'edit_subject_line': kwargs.edit_subject_line, 'msg_text': kwargs.msg_text, 'template_id': kwargs.template_id } });
            }
        }
        else if ('tg_subject_line' in kwargs) {
            if (kwargs.tg_template_id == null) {
                draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg } });
            } else {
                draganddropjson.push({ [data_id]: { 'tg_subject_line': kwargs.tg_subject_line, 'tg_msg': kwargs.tg_msg, 'tg_template_id': kwargs.tg_template_id } });
            }
        }
        else if ('delay' in kwargs) draganddropjson.push({ [data_id]: { 'delay': kwargs.delay } })
        else if ('goal' in kwargs) draganddropjson.push({ [data_id]: { 'goal': kwargs.goal } })
        else if ('trigger' in kwargs) draganddropjson.push({ [data_id]: { 'trigger': kwargs.trigger, 'trigger_time': kwargs.trigger_time, 'read_unread': kwargs.read_unread } })
    }
    document.getElementById('draganddropjson_for_data').value = JSON.stringify(draganddropjson);
}


function emailpopuponsubmit(e) {
    e.preventDefault();
    var template_id = $("#id_set_template").val();

    var button = document.getElementById("addEmailButton");
    var edit_subject_line = $("#edit_subject_line").val();
    var msg_text = $(`#txtEditor_1`).Editor("getText");
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);

    if (edit_subject_line == '') {
        $("#email-popup-alert-subjectline").show();
        setTimeout(function () {
            $("#email-popup-alert-subjectline").hide();
        }, 10000);

    } else if (msg_text == '') {
        $("#email-popup-alert-message").show();
        setTimeout(function () {
            $("#email-popup-alert-message").hide();
        }, 10000);
    } else {
        setdraganddropjson(draganddropjson, button, { 'edit_subject_line': edit_subject_line, 'msg_text': msg_text, 'template_id': template_id })

        document.getElementById('draganddropjson').value = JSON.stringify(draganddropjson)
        $('#addEmailModalCenter').modal('toggle');
        $("#email-popup")[0].reset();
        $(`#txtEditor_1`).Editor("setText", '')
    }
}

function telegrampopuponsubmit(e) {
    e.preventDefault();
    var tg_template_id = $("#tg_set_template").val();

    var button = document.getElementById("addTelegramButton");
    var tg_subject_line = $("#tg_subject_line").val();
    var tg_msg = $(`#tg_msg`).val();
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);

    if (tg_subject_line == '') {
        $("#telegram-popup-alert-subjectline").show();
        setTimeout(function () {
            $("#email-popup-alert-subjectline").hide();
        }, 10000);

    } else if (tg_msg == '') {
        $("#email-popup-alert-message").show();
        setTimeout(function () {
            $("#email-popup-alert-message").hide();
        }, 10000);
    } else {
        setdraganddropjson(draganddropjson, button, { 'tg_subject_line': tg_subject_line, 'tg_msg': tg_msg, 'tg_template_id': tg_template_id })

        document.getElementById('draganddropjson').value = JSON.stringify(draganddropjson)
        $('#addTelegramModalCenter').modal('toggle');
        $("#telegram-popup")[0].reset();
    }
}

function addtemplate(e) {
    e.preventDefault();

    var button = document.getElementById("addEmailButton");
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);
    var template_name = $('#template_name').val();

    if (template_name == '') {
        $("#email-popup-alert-template-name").show();
        setTimeout(function () {
            $("#email-popup-alert-template-name").hide();
        }, 10000);
    } else {
        setdraganddropjson(draganddropjson, button, { 'template_name': template_name })
        document.getElementById('draganddropjson').value = JSON.stringify(draganddropjson)
        $('#addTemplateNModalCenter').modal('toggle');
        $("#template-popup")[0].reset();
    }
}

function addtgtemplate(e) {
    e.preventDefault();

    var button = document.getElementById("addTelegramButton");
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);
    var tg_template_name = $('#tg_template_name').val();

    if (tg_template_name == '') {
        $("#email-popup-alert-template-name").show();
        setTimeout(function () {
            $("#email-popup-alert-template-name").hide();
        }, 10000);
    } else {
        setdraganddropjson(draganddropjson, button, { 'tg_template_name': tg_template_name })
        document.getElementById('draganddropjson').value = JSON.stringify(draganddropjson)
        $('#addTgTemplateNModalCenter').modal('toggle');
        $("#tgtemplate-popup")[0].reset();
    }
}

function delaypopuponsubmit(e) {
    e.preventDefault();

    var button = document.getElementById("addDelayButton");
    var delay = $("#delay").val();
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);

    if (delay == '') {
        $("#delay-popup-alert-delay").show();
        setTimeout(function () {
            $("#delay-popup-alert-delay").hide();
        }, 10000);
    } else {

        setdraganddropjson(draganddropjson, button, { 'delay': delay })

        document.getElementById(`draganddropjson`).value = JSON.stringify(draganddropjson);
        $('#addDelayModalCenter').modal('toggle');
        $("#delay-popup")[0].reset();
    }
}


function goalpopuponsubmit(e) {
    e.preventDefault();

    var button = document.getElementById("addGoalButton");
    var goal = $("#goal").val();
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);

    if (goal == '') {
        $("#goal-popup-alert-goal").show();
        setTimeout(function () {
            $("#goal-popup-alert-goal").hide();
        }, 10000);
    } else {
        setdraganddropjson(draganddropjson, button, { 'goal': goal })

        document.getElementById(`draganddropjson`).value = JSON.stringify(draganddropjson);
        $('#addGoalModalCenter').modal('toggle');
        $("#goal-popup")[0].reset();
    }
}

function triggerpopuponsubmit(e) {
    e.preventDefault();

    var button = document.getElementById("addTriggerButton");
    var trigger = $("#trigger").val();
    var trigger_time = $("#trigger-time").val();
    var read_unread = document.getElementById("read_unread").checked;
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);

    if (trigger == '') {
        $("#trigger-popup-alert-trigger").show();
        setTimeout(function () {
            $("#trigger-popup-alert-trigger").hide();
        }, 10000);
    } else {
        setdraganddropjson(draganddropjson, button, { 'trigger': trigger, 'trigger_time': trigger_time, 'read_unread': read_unread })

        document.getElementById(`draganddropjson`).value = JSON.stringify(draganddropjson);
        $('#addTriggerModalCenter').modal('toggle');
        $("#trigger-popup")[0].reset();
    }
}

function emailformreset() {
    $("#email-popup")[0].reset();
    $(`#txtEditor_1`).Editor("setText", '')
}

function telegramformreset() {
    $("#telegram-popup")[0].reset();
}

function delayformreset() {
    $("#delay-popup")[0].reset();
}

function goalformreset() {
    $("#goal-popup")[0].reset();
}

function triggerformreset() {
    $("#trigger-popup")[0].reset();
}

function set_data(draganddropjson, event, node_key) {
    for (let [key, value] of Object.entries(draganddropjson)) {
        for (let [k, v] of Object.entries(value)) {
            if (k == node_key) {
                if (event == 'email') set_text_email(v.edit_subject_line, v.msg_text, v.template_id)
                if (event == 'telegram') set_text_telegram(v.tg_subject_line, v.tg_msg, v.template_id)
                if (event == 'delay') set_text_delay(v.delay);
                if (event == 'goal') set_text_goal(v.goal)
                if (event == 'trigger') set_text_trigger(v.trigger, v.trigger_time, v.read_unread)
            }
        };
    };
}

function set_text_email(subject_line, text, template_id) {
    $("#id_set_template").val(template_id);
    $("#edit_subject_line").val(subject_line);
    $('#txtEditor_1').Editor("setText", text)
}

function set_text_telegram(subject_line, text, template_id) {
    $("#tg_set_template").val(template_id);
    $("#tg_subject_line").val(subject_line);
    $('#tg_msg').val(text)
}

function set_text_delay(delay) {
    $("#delay").val(parseInt(delay))
}

function set_text_goal(goal) {
    $("#goal").val(goal)
}

function set_text_trigger(trigger, trigger_time, read_unread) {
    $("#trigger").val(trigger);
    $("#trigger-time").val(trigger_time);
    document.getElementById("read_unread").checked = read_unread;
}

function setbuttonattributes(diagram_json, button, node_key) {
    button.setAttribute('data-template-id', node_key);
    for (let [key, value] of Object.entries(diagram_json.linkDataArray)) {
        if (value.to == node_key) {
            button.setAttribute('before-data-id', value.from);
            if ((Math.abs(value.points[0]) - Math.abs(value.points[2])) == 0) button.setAttribute('data-loc', 'yes');
            else button.setAttribute('data-loc', 'no');
        }
    }
}


function add_draganddrgopjson_default(popup) {
    var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);
    var emailbutton = document.getElementById("addEmailButton");
    var telegrambutton = document.getElementById("addTelegramButton");
    var delaybutton = document.getElementById("addDelayButton");
    var goalbutton = document.getElementById("addGoalButton");
    var triggerbutton = document.getElementById("addTriggerButton");
    switch (popup) {
        case "EMAIL_TEMPLATE":
            setdraganddropjson(draganddropjson, emailbutton, { 'edit_subject_line': '', 'msg_text': '' })
            document.getElementById('draganddropjson').value = JSON.stringify(draganddropjson)
            break;
        case "TELEGRAM":
            setdraganddropjson(draganddropjson, telegrambutton, { 'tg_subject_line': '', 'tg_msg': '' })
            document.getElementById('draganddropjson').value = JSON.stringify(draganddropjson)
            break;
        case "DELAY":
            setdraganddropjson(draganddropjson, delaybutton, { 'delay': '' })
            document.getElementById(`draganddropjson`).value = JSON.stringify(draganddropjson);
            break;
        case "GOAL":
            setdraganddropjson(draganddropjson, goalbutton, { 'goal': '' })
            document.getElementById(`draganddropjson`).value = JSON.stringify(draganddropjson);
            break;

        case "TRIGGER":
            setdraganddropjson(draganddropjson, triggerbutton, { 'trigger': '', 'trigger_time': '', 'read_unread': '' })
            document.getElementById(`draganddropjson`).value = JSON.stringify(draganddropjson);
            break;
    }
}

function draganddrop_check(e) {
    e.preventDefault();
    var result = true
    email_or_tg = false;
    var draganddropjson = JSON.parse(document.getElementById('draganddropjson_for_data').value);
    if (Object.values(draganddropjson).length != 0) {
        for (let [key, value] of Object.entries(draganddropjson)) {
            for (let [k, v] of Object.entries(value)) {
                if ('edit_subject_line' in v) {
                    email_or_tg = true;
                    if (v.edit_subject_line == '') {
                        result = false;
                        $("#email-popup-alert-subjectline").show();
                        setTimeout(function () {
                            $("#email-popup-alert-subjectline").hide();
                        }, 10000);

                    } else if (v.msg_text == '') {
                        result = false;
                        $("#email-popup-alert-message").show();
                        setTimeout(function () {
                            $("#email-popup-alert-message").hide();
                        }, 10000);
                    }
                } else if ('tg_subject_line' in v) {
                    email_or_tg = true;
                    if (v.tg_subject_line == '') {
                        result = false;
                        $("#email-popup-alert-subjectline").show();
                        setTimeout(function () {
                            $("#email-popup-alert-subjectline").hide();
                        }, 10000);

                    } else if (v.tg_msg == '') {
                        result = false;
                        $("#email-popup-alert-message").show();
                        setTimeout(function () {
                            $("#email-popup-alert-message").hide();
                        }, 10000);
                    }
                } else if ('delay' in v) {
                    if (v.delay == '') {
                        result = false;
                        $("#delay-popup-alert-delay").show();
                        setTimeout(function () {
                            $("#delay-popup-alert-delay").hide();
                        }, 10000);
                    }
                } else if ('goal' in v) {
                    if (v.goal == '') {
                        result = false;
                        $("#goal-popup-alert-goal").show();
                        setTimeout(function () {
                            $("#goal-popup-alert-goal").hide();
                        }, 10000);
                    }
                } else if ('trigger' in v) {
                    if (v.trigger == '') {
                        result = false;
                        $("#trigger-popup-alert-trigger").show();
                        setTimeout(function () {
                            $("#trigger-popup-alert-trigger").hide();
                        }, 10000);
                    }
                }
            }
        }
    } else {
        result = false;
        $("#newsletter-alert-empty").show();
        setTimeout(function () {
            $("#newsletter-alert-empty").hide();
        }, 10000);
    }
    if (!email_or_tg) {
        result = false;
        $("#newsletter-alert-empty").show();
        setTimeout(function () {
            $("#newsletter-alert-empty").hide();
        }, 10000);
    }
    return result
}


function diagram_delete_node(diagram, node) {
    diagram.startTransaction();
    diagram.remove(node);
    diagram.commitTransaction("deleted node");
}

function show_trigger_first_alert() {
    $("#trigger-popup-alert-first").show();
    setTimeout(function () {
        $("#trigger-popup-alert-first").hide();
    }, 10000);
}

function show_trigger_error_alert(type) {
    $(`#trigger-popup-alert-${type}`).show();
    setTimeout(function () {
        $(`#trigger-popup-alert-${type}`).hide();
    }, 10000);
}