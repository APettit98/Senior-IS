form_count = Number($("#count").val());
target_element = $("#form_fields");

$("#button-id-add").click(function(){
    form_count ++;

    addressNumber = (form_count + 3).toString();
    id = 'id_location' + addressNumber;

   $("<div class='form-row form-row'> " +
     "<div class='col form-group'> " +
     "<div class='form-group row'> " +
     "<div class=''> " +
     `<input type="text" name=${"location" + addressNumber} class="textinput textInput form-control" id=${id}>` +
     "</div></div></div></div>").insertBefore($("#button-row"));

    $(`#${id}`).attr('placeholder', "Address " + addressNumber);
    $("#count").val += 1;
});
