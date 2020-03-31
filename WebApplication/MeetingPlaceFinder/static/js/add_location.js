//form_count = Number($("#count").val());
//target_element = $("#form_fields");
//
//$("#button-id-add").click(function(){
//    form_count ++;
//
//    addressNumber = (form_count + 3).toString();
//    id = 'id_location' + addressNumber;
//
//   $("<div class='form-row form-row'> " +
//     "<div class='formColumn form-group'> " +
//     "<div class='form-group row'> " +
//     "<div class=''> " +
//     `<input type="text" name=${"location" + addressNumber} class="textinput textInput form-control" id=${id}>` +
//     "</div></div></div></div>").insertBefore($("#button-row"));
//
//    $(`#${id}`).attr('placeholder', "Address " + addressNumber);
//    $("#count").val = form_count;
//});

function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    newElement.find(':input:not([type=button]):not([type=submit]):not([type=reset])').each(function() {
        if((this.name).includes('-' + (total-1) + '-')){
            var name = $(this).attr('name').replace('-' + (total-1) + '-', '-' + total + '-');
        }
        else{

        }
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var forValue = $(this).attr('for');
        if (forValue) {
          forValue = forValue.replace('-' + (total-1) + '-', '-' + total + '-');
          $(this).attr({'for': forValue});
        }
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    var conditionRow = $('.form-row.location-row:not(:last)');
    conditionRow.find('.btn.add-form-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-form-row').addClass('remove-form-row')
    .html('<span class="glyphicon glyphicon-minus" aria-hidden="true"></span>');
    return false;
}

function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 3){
        btn.closest('.form-row.location-row').remove();
        var forms = $('.form-row.location-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    return false;
}

$(document).on('click', '.add-form-row', function(e){
    e.preventDefault();
    cloneMore('.form-row.location-row:last', 'form');
    return false;
});

$(document).on('click', '.remove-form-row', function(e){
    e.preventDefault();
    deleteForm('form', $(this));
    return false;
});