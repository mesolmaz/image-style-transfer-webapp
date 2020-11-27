

$(document).ready(function(){ 
    $("select").imagepicker({
          show_label:   true,
          clicked:function(){
            console.log($(this).find("option[value='" + $(this).val() + "']").data('img-src'));
            var image_url = $(this).find("option[value='" + $(this).val() + "']").data('img-src');
            $.post("/styleimage", {imageurl:image_url}).done();
            // $.post("/createart", {imageurl:image_url}).done();
          }
        });
     });    

