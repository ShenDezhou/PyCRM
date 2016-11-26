$(function() {
    var element = document.getElementById('editor_holder');


    // This is the starting value for the editor
    // We will use this to seed the initial editor 
    // and to provide a "Restore to Default" button.
    // var starting_value = [{"tag":"Novice","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[1,1,1]},{"tag":"BigGuy","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]},{"tag":"Archer","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]},{"tag":"Rider","pos":[0.0,0.0,0.0],"speed":10.3,"interval":[10.0]},{"tag":"FlyMan","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]},{"tag":"Novice","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]},{"tag":"BigGuy","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]},{"tag":"Archer","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]},{"tag":"Rider","pos":[0.0,0.0,0.0],"speed":10.3,"interval":[10.0]},{"tag":"FlyMan","pos":[0.0,0.0,0.0],"speed":3.3,"interval":[]}];
    var schema = {
        "type": "array",
        "format": "table",
        "items": {
            "type": "object",
            "properties": {
                "tag": {
                    "type": "string"
                },
                "pos": {
                    "type": "array",
                    "format": "table",
                    "items": {
                        "type": "number"
                    }
                },
                "speed": {
                    "type": "number"
                },
                "interval": {
                    "type": "array",
                    "format": "table",
                    "items": {
                        "type": "integer"
                    }
                }

            }
        }
    };

    JSONEditor.defaults.theme = 'bootstrap3';
    JSONEditor.defaults.iconlib = 'fontawesome4';
    JSONEditor.plugins.select2.enable = true;
    var editor = new JSONEditor(element, {
        schema: schema
    });
    $.ajax({
        type: "GET",
        url: '/rest/duohero/level',
        cache: true,
        data: {

        },
        success: function(data) {
            editor.setValue(data);
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });
    $('#submit').click(function() {
        var data = JSON.stringify(editor.getValue());
        data = data.replace(/null/g, "0.0");
        console.log(data);
        $.ajax({
            type: "POST",
            url: '/rest/duohero/level/commit',
            cache: false,
            data: {
                st_value: data
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
