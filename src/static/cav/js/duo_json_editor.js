$(function() {
    var element = document.getElementById('editor_holder');


    // This is the starting value for the editor
    // We will use this to seed the initial editor 
    // and to provide a "Restore to Default" button.
    var starting_value = [{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[5,5]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[0,0]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,0]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,3]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[0,0]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,0]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,2]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[1,1]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[0,0]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[0,0]}}},{"wavesL":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[3,6]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[0,3]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[10,12]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[11,11]}},"wavesR":{"Enemy_Novice":{"name":"Enemy_Novice","amount":[4,7]},"Enemy_BigGuy":{"name":"Enemy_BigGuy","amount":[1,4]},"Enemy_Archer":{"name":"Enemy_Archer","amount":[1,4]},"Enemy_Rider":{"name":"Enemy_Rider","amount":[10,10]},"Enemy_FlyMan":{"name":"Enemy_FlyMan","amount":[10,10]}}}];
    JSONEditor.defaults.theme = 'bootstrap3';
    JSONEditor.defaults.iconlib = 'bootstrap3';
    JSONEditor.plugins.selectize.enable = true;
    var editor = new JSONEditor(element,{
      schema: starting_value
    });
    $.ajax({
            type: "GET",
            url: '/rest/duohero/level',
            cache: true,
            data: {
                
            },
            success: function(data) {
                // $("#editor_holder").jsoneditor({schema:data});
                // $("#editor_holder").jsoneditor('value',data);
                editor.setValue(data);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    $('#submit').click(function() {
        var data =JSON.stringify(editor.getValue());
        console.log(data);
        $.ajax({
            type: "POST",
            url: '/rest/duohero/level/commit',
            cache: false,
            data: {
                st_value:data
            },
            success: function(data) {
                alert(data.message);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });

});
