// Send tree JSON to Python and create links to exorted files
$(function() {
    $('button#save').bind('click', function() {
        var v = $('#treediv').jstree(true).get_json()
        var tree = JSON.stringify(v);

        $.ajax({
            method: "POST",
            contentType: "application/json",
            url: "{{ url_for('save_columnsfile', studiesfolder=studiesfolder, study=study) }}",
            data: tree
        })
        .done(function( msg ) {
            console.log( "Data Saved: " + msg.feedback.infos );
            document.getElementById("feedbacksave").innerHTML = '<ul class="feedback" id="feedbacklist"></ul>';
    for (i = 0; i < msg.feedback.errors.length; i++) {
        $( "#feedbacklist" ).append( "<li class='error'>"+msg.feedback.errors[i]+"</li>" );
    }
    for (i = 0; i < msg.feedback.warnings.length; i++) {
        $( "#feedbacklist" ).append( "<li class='warning'>"+msg.feedback.warnings[i]+"</li>" );
    }
    for (i = 0; i < msg.feedback.infos.length; i++) {
        $( "#feedbacklist" ).append( "<li class='message'>"+msg.feedback.infos[i]+"</li>" );
    }
        })
  .fail(function() {
    document.getElementById("feedbacksave").innerHTML = '<ul class="feedback" id="feedbacklist"></ul>';
    $( "#feedbacklist" ).append( "<li class='error'>Error encountered in saving column mapping file</li>" );
  });

        return false;
    });
});

var node;

$("form#datanodedetails").submit(function (e) {
    e.preventDefault();

    if (typeof node != 'undefined') {

        var text = $( "input[name='datalabel']" ).val();
        var updated = $("#treediv").jstree('rename_node', node , text );
        var type = $("select[name='nodetype']").val();
        $("#treediv").jstree('set_type', node , type );
        enableRightFields(type);

        if (typeof node.data == 'undefined') {
            node.data = {}
        }

        node.data['Filename']           = $( "input[name='filename']"         ).val();
        node.data['Column Number']      = $( "input[name='columnnumber']"     ).val();
        node.data['Data Label Source']  = $( "input[name='datalabelsource']"  ).val();
        node.data['Control Vocab Cd']   = $( "input[name='controlvocabcd']"   ).val();
        node.data['tag_description']    = $( "input[name='tag_description']"  ).val();
        if (updated) {feedback("Successfully applied", false)}
    } else if (typeof node == 'tag') {
        // do something here to populate node.data.tags dictionary.

    } else {feedback("No node selected", true)}
});

function enableRightFields(type){
    if (type == 'numeric' | type == 'categorical'){
        $('.clinicaldata').prop('hidden', false);
        $('.tagdata').prop('hidden', true);
    } else if (type == 'tag'){
        $('.tagdata').prop('hidden', false);
        $('.clinicaldata').prop('hidden', true);
    } else {
        $('.tagdata').prop('hidden', true);
        $('.clinicaldata').prop('hidden', true);
    }
}

function feedback(string, error) {
    $( "span#feedback" ).html(string).show();
    if (error) {
        $( "span#feedback" ).css('color', 'red');
    } else {
        $( "span#feedback" ).css('color', 'green');
    }
    setTimeout(function() {
        $( "span#feedback" ).fadeOut(function () {
            $( "span#feedback" ).html("");
        })
    }, 2000);
}


    // Create the tree
    $('#treediv')
    // listen for event
    .on('select_node.jstree', function (e, data) {
        node = data.instance.get_node(data.selected[0]);
        $( "form#datanodedetails" )[0].reset();
        $( "input[name='datalabel']" ).val(node.text);
        $( "select[name='nodetype']" ).val(node.type);

        enableRightFields(node.type);

        if (typeof node.data !== 'undefined') {
            $( "input[name='filename']" ).val(node.data['Filename']);
            $( "input[name='columnnumber']" ).val(node.data['Column Number']);
            if (typeof node.data['Data Label Source'] !== 'undefined') {
                $( "input[name='datalabelsource']" ).val(node.data['Data Label Source']);
            }
            if (typeof node.data['Control Vocab Cd'] !== 'undefined') {
                $( "input[name='controlvocabcd']" ).val(node.data['Control Vocab Cd']);
            }
            if (typeof node.data['tag_description'] !== 'undefined') {
                $( "input[name='tag_description']" ).val(node.data['tag_description']);
            }
        }
    })
    // create the instance
    .jstree({
        'core' : {
            'data' : json_data,
            "check_callback" : true
        },
         'dnd' : {
                    'is_draggable' : function(node) {
                        console.log('is_draggable called: ', node[0]);
                        if (node[0].type == 'alpha') {
                            return false;
                        }
                        return true;
                 }
        },
        "types" : {
            "default" : {
                "icon" : "/static/img/tree/folder.gif",
                "valid_children" : ["alpha",
                                    "numeric",
                                    "highdim",
                                    "codeleaf",
                                    "default",
                                    "categorical",
                                    "tag"]
            },
            "study" : {
                "icon" : "/static/img/tree/study.png",
                "valid_children" : "all"
            },
            "alpha" : {
                "icon" : "/static/img/tree/alpha.gif",
                "valid_children" : ["tag"]
            },
            "categorical" : {
                "max_depth" : "2",
                "icon" : "/static/img/tree/folder.gif",
                "valid_children" : ["alpha", "tag"]
            },
            "numeric" : {
                "icon" : "/static/img/tree/numeric.gif",
                "valid_children" : ["tag"]
            },
            "highdim" : {
                "icon" : "/static/img/tree/dna_icon.png",
                "valid_children" : ["tag"]
            },
            "tag" : {
                "icon" : "/static/img/tree/tag_icon.png",
                "valid_children" : "none"
            },
            "codeleaf" : {
                "icon" : "/static/img/tree/code.png",
                "valid_children" : ["alpha", "tag"]
            },
        },
        'sort': function (a, b) {
            if ((this.get_type(a) == 'default') && (this.get_type(b) != 'default')) {
                return -1;
            } else if ((this.get_type(a) != 'default') && (this.get_type(b) == 'default')) {
                return 1;
            } else if ((this.get_type(a) == 'tag') && (this.get_type(b) != 'tag')) {
                return -1;
            } else if ((this.get_type(a) != 'tag') && (this.get_type(b) == 'tag')) {
                return 1;
            } else {
                return this.get_text(a) > this.get_text(b) ? 1 : -1;
            }
        },

        "plugins" : [ "dnd", "sort", "contextmenu", "types", "unique"]
    }
});