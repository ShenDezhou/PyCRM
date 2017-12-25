$(function() {
    var element = $('#editor_holder');

    var editor = new JSONEditor(element, {
        ajax: true,
        refs: { "/duohero/level" },
        theme: 'bootstrap3',
        schema: {
          type: "object",
          title: "Car",
          properties: {
            make: {
              type: "string",
              enum: [
                "Toyota",
                "BMW",
                "Honda",
                "Ford",
                "Chevy",
                "VW"
              ]
            },
            model: {
              type: "string"
            },
            year: {
              type: "integer",
              enum: [
                1995,1996,1997,1998,1999,
                2000,2001,2002,2003,2004,
                2005,2006,2007,2008,2009,
                2010,2011,2012,2013,2014
              ],
              default: 2008
            }
          }
        }

    });

    editor.on('ready', function() {
        // Now the api methods will be available
        editor.validate();
    });
});
