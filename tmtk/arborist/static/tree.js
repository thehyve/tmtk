var node, jstree, tagBuffer;

// Add jstree json to the submit form as hidden parameter.
$("#edit_form").submit( function() {
    var tree = stringTree();
    $('<input />').attr('type', 'hidden')
        .attr('name', 'json')
        .attr('id', 'id_json')
        .attr('value', tree)
        .appendTo('#edit_form');
    return true;
});

// use the download function to download a treefile with the name of the study. HTML5 stuff.
$('button#download').click( function() {
    serveDownload(study_name.toString() + '.treefile', stringTree() )
});

function serveDownload(filename, text) {
    var pom = document.createElement('a');
    var url = URL.createObjectURL( new Blob( [text], {type:'text/plain'} ) );
    pom.setAttribute('href', url);
    pom.setAttribute('download', filename);

    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    }
    else {
        pom.click();
    }
}

// Keep this for the embedded return from Jupyter Notebooks
$(function () {
  $('button#embeded_return').bind('click', function () {
    var tree = stringTree();

    $.ajax({
          method: "POST",
          contentType: "application/json",
          url: shutdown_url,
          data: tree
        })
        .fail(function () {
          document.getElementById("feedbacksave").innerHTML = '<ul class="feedback" id="feedbacklist"></ul>';
          $("#feedbacklist").append("<li class='error'>Error encountered in saving column mapping file</li>");
        });

    return false;
  });
});

// Gets a minimal string version of the current tree
function stringTree(){
    var v = jstree.get_json('#', {'no_state': true});
    return JSON.stringify(v, replacer);
}

// This function is used by JSON.stringify to exclude unnecessary nodes.
function replacer(key, value) {
    var skipped = ['icon', 'li_attr', 'a_attr'];
    if ($.inArray(key, skipped) > -1 ||
            (key == 'type' && value == 'default')) {
        return undefined;
    }
    return value;
}

// use the download function to download a treefile with the name of the study. HTML5 stuff.
$('button#download-template').click( function (obj) {
    showAlert("Created template from current tree.");
    console.log('Downloading template.');
    serveDownload('arborist_template.txt', stringTreeTemplate() );
});

// Gets a template version of the current tree
function stringTreeTemplate(){
    var v = jstree.get_json('#', {'no_state': true});
    return JSON.stringify(v, replacerTemplate);
}

// This function is used by JSON.stringify to exclude unnecessary information.
function replacerTemplate(key, value) {
    var skipped = ['icon', 'li_attr', 'a_attr', 'id', 'state'];
    if ($.inArray(key, skipped) > -1 |
            (key == 'type' && value != 'tag') ||
            (key == 'children' && value.length === 0) ||
            (key == 'data' && !value.tags)) {
        return undefined;
    }
    return value;
}

// Button to check if tag table is filled and if so add new tag
function add_tags_feedback () {
    //.find(":input") will also find description textarea fields.
    var empty = $('#tagtable-body').find(":input").filter(function() {
        return this.value === "";
    });
    if (empty.length) {
        feedback("Fill all fields to add new row.", true);
    } else {
        createTagRow();
        feedback("Tags added.", false);
    }
}

function color_bg (id, color) {
    var item = document.getElementById(id);
    if (item) {
        item.style.backgroundColor = color;
        setTimeout(function () {item.style.backgroundColor = ""; }, 2000 );

    }
}

function field_update (id) {
    color_bg(id, '#bafbaf')
}

function field_empty (id) {
    color_bg(id, '#ffc3c3')
}

function process_tags (obj) {
    // Reset tags object to clear all existing tags
    var old_tags = node.data.tags;
    node.data.tags = {};
    var rowCount = $("#tagtable-body tr").length;

    var i;
    for (i = 1; i <= rowCount; i++) {
        var title = $("#tagname_" + i).val();
        var desc = $("#tagdesc_" + i).val();
        var weight = $("#tagweight_" + i).val();


        if (title === "" && desc !== "") {
            field_empty('tagname_' + i);
        } else if (desc === "" && title !== "") {
            field_empty('tagdesc_' + i);
        }

        var entry = old_tags[title];
        if (typeof entry !== 'undefined') {
            if ((desc !== "") && (entry[0] !== desc)){
                field_update("tagdesc_" + i);
            }
            if ((weight !== "") && (entry[1] !== weight)){
                field_update("tagweight_" + i);
            }
        } else if (title !== "" && desc !== "") {
            field_update("tagname_" + i);
            field_update("tagdesc_" + i);
            field_update("tagweight_" + i);
        }

        // If title and description are present, store it to the tags.
        if ( title !== "" && desc !== "" && typeof title !== "undefined" && typeof desc !=="undefined") {
            if (weight === "") {
                weight = 3
            }
            console.log('Adding tag: ' + title + ': ' + desc + ' (' + weight + ').');
            node.data.tags[title] = [desc, weight];
        }
    }
    add_tags_feedback()
}

$("form#datanodedetails").submit(function (e) {
    e.preventDefault();
    if (node.type == 'tag') {
        process_tags();
        return;
    }
    var new_label = $("#datalabel").val();
    var updated = jstree.rename_node(node, new_label);

    if (node.type != 'default'){

        if (typeof node.data == 'undefined') {
            node.data = {};
        }

        node.data['m5'] = $("#magic5").val();
        node.data['m6'] = $("#magic6").val();
        node.data['cty'] = $("#fc").prop('checked') ? 'CATEGORICAL' : '';

        var new_type;

        if (updated) {
            var is_special = ['SUBJ_ID', 'OMIT'].indexOf(new_label) > -1;

            // If the node text starts with OMIT, change the type (and icon)
            if (is_special && (['categorical', 'numeric', 'empty'].indexOf(node.type) > -1 )) {
                new_type = 'codeleaf';
                // If changed from SUBJ_ID or OMIT to regular, change type back to original
            } else if ((node.type == 'codeleaf') && (!is_special)) {
                new_type = node.data['ctype'];
            }
            jstree.set_type(node, new_type);

        }
    }
});

function enableRightFields(type) {
    if ($.inArray(type, ['numeric', 'categorical', 'codeleaf', 'empty']) > -1) {
        $('.label').prop('hidden', false);
        $('.clinicaldata').prop('hidden', false);
        $('.tag-container').prop('hidden', true);
        $('.hdtagdata').prop('hidden', true);
        $('.dfv').prop('hidden', true);
    } else if (type == 'tag') {
        console.log('Enable tags fields.');
        $('.tag-container').prop('hidden', false);
        $('.clinicaldata').prop('hidden', true);
        $('.label').prop('hidden', true);
        $('.hdtagdata').prop('hidden', true);
        $('.dfv').prop('hidden', true);
    } else if (type == 'highdim') {
        console.log('Enable highdim fields.');
        $('.tag-container').prop('hidden', true);
        $('.clinicaldata').prop('hidden', true);
        $('.hdtagdata').prop('hidden', false);
        $('.label').prop('hidden', false);
        $('.dfv').prop('hidden', true);
    } else {
        $('.label').prop('hidden', false);
        $('.tag-container').prop('hidden', true);
        $('.hdtagdata').prop('hidden', true);
        $('.clinicaldata').prop('hidden', true);
        $('.dfv').prop('hidden', true);
    }
}

function feedback(string, error) {
  $("span#feedback").html(string).show();
  if (error) {
    $("span#feedback").css('color', 'red');
  } else {
    $("span#feedback").css('color', 'green');
  }
  setTimeout(function () {
    $("span#feedback").fadeOut(function () {
      $("span#feedback").html("");
    })
  }, 2000);
}

function customMenu(node) {
    // The default set of all items
    var items = {
        createItem: { // The "create" menu item
            label: "Create node",
            action: function (data) {
                var inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                inst.create_node(obj, {}, "last", function (new_node) {
                    new_node.data = {file: true};
                    setTimeout(function () {
                        inst.edit(new_node);
                    }, 0);
                });
            }
        },
        addTags: { // The "Add tags" menu item
            label: "Add tags",
            action: function (data) {
                var tag_specs = {
                    type: 'tag',
                    text: 'Tags',
                    data: {
                        'tags': {}
                    }
                };
                jstree.create_node(node, tag_specs, "first", function (new_node) {

                    setTimeout(function () {
                        jstree.deselect_all();
                        jstree.select_node(new_node);
                    }, 100);
                });
            }
        },
        copyTags: {
            label: "Copy Tags",
            action: function (data) {
                tagBuffer = node.data;
                console.log('Copying node.');
            }
        },
        pasteTags: {
            label: "Paste Tags",
            action: function (data){

                var tagNode;
                // if not tag selected, check if has tag child
                tagNode = node.type == 'tag' ? node : jstree.get_node(node.children[0]);

                // if not tag child, create one.
                if (tagNode.type != "tag") {
                    jstree.create_node(node, {"tags": {}, "type": 'tag', "text": "Tags"}, "first", function(new_node){
                        console.log('pasting into: ', new_node);
                        tagNode = new_node;
                    });
                }
                tagNode.data = jQuery.extend(true, {}, tagBuffer, tagNode.data);
                jstree.deselect_all();
                jstree.select_node(tagNode);
            }
        },
        deleteItem: { // The "delete" menu item
            label: "Delete",
            action: function (data) {
                var inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                if (inst.is_selected(obj)) {
                    inst.delete_node(inst.get_selected());
                }
                else {
                    inst.delete_node(obj);
                }
            }
        }
    };
    if (node.type != 'tag'){
        delete items.copyTags;
    } else {
        delete items.addTags;
    }
    if (!tagBuffer) {
        delete items.pasteTags;
    }
    return items;
}

function createTagRow(){
    // Add new row to tags table and return the row number
    var rowCount = $("#tagtable-body tr").length;
    var counter = rowCount / 2 + 1;

    var title_id = 'tagname_' + counter;
    var desc_id = 'tagdesc_' + counter;
    var weight_id = 'tagweight_' + counter;

    var tdInput = '<input placeholder="Title..." type="text" class="form-control form-control-sm tag-title" id="' + title_id + '" />';
    var tdDesc = '<textarea placeholder="Description..." class="form-control form-control-sm tag-description" rows="1" id="' + desc_id + '" />';
    var tdWeight = '<input type="number" class="form-control form-control-sm tag-weight" min="1" max="10" value="3" id="' + weight_id +'" />';

    var tr = $('<tr></tr>')
        .append('<td style="padding-left: 5px;" >'+tdInput+'</td>')
        .append('<td style="padding-right: 5px;">'+tdWeight+'</td>');

    var tagtableBody = $("#tagtable-body");
    tagtableBody.append(tr);
    tagtableBody.append('<tr><td colspan=2 style="padding-left:5px;padding-right:5px;" >'+tdDesc+'</td></tr>');

    $('#' + title_id).focus();

    return counter
}

$("#tagbox").on("keypress", ".tag-description" , function(e) {
        if ((e.keyCode || e.which) == 13) {
            $(this).parents('form').submit();
        e.preventDefault();
        }
    });

var keymap = {default : 'Folder',
              numeric : 'Numerical',
              alpha : 'Categorical Value',
              categorical : 'Categorical',
              tag : 'Metadata tags',
              highdim : 'High-dimensional',
              codeleaf : 'Special concept',
              empty: 'Empty node'
             };
function prettyType(label){
    return keymap[label]
}

$(function () {
    var to = false;
    $('#search_box').keyup(function () {
        var spinner = $("#search_spinner");
        spinner.show();
        var v = $('#search_box').val();
        if(to) { clearTimeout(to); }
        to = setTimeout(function () {
            jstree.search(v);
        }, 400);
        if(!v.length){
            spinner.hide();
        }
    });
});

// Create the tree
$('#tree-div')
// listen for event
    .on('loaded.jstree', function() {
        jstree = $(this).jstree(true);
        $("#search_spinner").hide();
        jstree.select_node('ul > li:first');
      })
    .on('search.jstree', function() {
      $("#search_spinner").hide();
      })
    .on('keydown.jstree', '.jstree-anchor', $.proxy(function (e) {
        if (e.target.tagName === "INPUT") {
            return true;
        }
        var o;
        e.preventDefault();
        o = jstree.get_node(e.currentTarget);
        if (e.which === 46 || e.which === 8) {
            // remove node with forward or backward delete
            if (o == "#") {
                showAlert("Cannot remove root nodes.");
                return undefined;
            }
            if (o && o.id && o.id !== "#") {
                o = jstree.is_selected(o) ? jstree.get_selected() : o;
                jstree.delete_node(o);
            }
        } else if (e.which === 13) {
            // edit current node with enter
            jstree.deselect_all();
            jstree.select_node(o);
            if (node.type != 'tag'){
                jstree.edit(o, null, function (new_node, status) {
                    $("#datalabel").val(new_node.text);
                    $("form#datanodedetails").submit(); // To make changes to nodes if applicable.
                });
            }
        } else if (e.which === 32) {
            // select node with space
            jstree.deselect_all();
            jstree.select_node(o);
        }
    }))
    .on('select_node.jstree', function (e, data) {
      node = data.instance.get_node(data.selected[0]);
      $("form#datanodedetails")[0].reset();
      $("#datalabel").val(node.text);
      $("#nodetype").text(prettyType(node.type));

      enableRightFields(node.type);

      if (node.data != null) {
        $("#filename").text(node.data['fn']);
        $("#columnnumber").text(node.data['col']);
        if (typeof node.data['m5'] !== 'undefined') {
          $("#magic5").val(node.data['m5']);
        }
        if (typeof node.data['m6'] !== 'undefined') {
          $("#magic6").val(node.data['m6']);
        }
        if (node.data['cty'] === 'CATEGORICAL') {
          $("#fc").prop('checked', true);
        }
        if ((node.type == 'alpha') && (node.data['dfv'] !== node.text)) {
          $('.dfv').prop('hidden', false);
          $("#datafile_value").text(node.data['dfv']);
        }
        if ((node.type == 'highdim') && (node.data.hd_args !== 'undefined')) {
          $("#hd_type").text(node.data.hd_args['hd_type']);
          $("#hd_sample").text(node.data.hd_args['hd_sample']);
          $("#hd_tissue").text(node.data.hd_args['hd_tissue']);
          $("#pl_genome_build").text(node.data.hd_args['pl_genome_build']);
          $("#pl_id").text(node.data.hd_args['pl_id']);
          $("#pl_marker_type").text(node.data.hd_args['pl_marker_type']);
          $("#pl_title").text(node.data.hd_args['pl_title']);
        }

        // This way to add multiple tags to 'tags' dictionary in 'data'
        if (typeof node.data['tags'] !== 'undefined') {
          // Clear the existing tag table
          $('#tagtable-body').empty();
          // Populate tags
          for (var key in node.data.tags) {
            if (node.data.tags.hasOwnProperty(key)) {
                var counter = createTagRow();

                var title_id = 'tagname_' + counter;
                var desc_id = 'tagdesc_' + counter;
                var weight_id = 'tagweight_' + counter;

                $('#' + title_id).val(key);
                $('#' + desc_id).val(node.data.tags[key][0]);
                $('#' + weight_id).val(node.data.tags[key][1]);
            }
          }
          // Add single empty row
          createTagRow();
        }
      }
    })
    // create the instance
    .jstree({
      'core': {
        'data': treeData,
        "check_callback": true
      },
      'dnd': {
        'is_draggable': function (node) {
          console.log('is_draggable called: ', node[0]);
          return (node[0].type != 'alpha');
        }
      },
      "unique": {case_sensitive : true},
      "contextmenu": {items: customMenu},

      "types": {
        "default": {
          "icon": "/static/images/tree/folder.gif"
        },
        "alpha": {
          "icon": "/static/images/tree/alpha.gif",
          "valid_children": ["tag"]
        },
        "categorical": {
          "icon": "/static/images/tree/folder.gif"
        },
        "numeric": {
          "icon": "/static/images/tree/numeric.gif",
          "valid_children": ["tag"]
        },
        "highdim": {
          "icon": "/static/images/tree/dna_icon.png",
          "valid_children": ["tag"]
        },
        "empty": {
          "icon": "/static/images/tree/empty.png"
        },
        "tag": {
          "icon": "/static/images/tree/tag_icon.png",
          "valid_children": "none"
        },
        "codeleaf": {
          "icon": "/static/images/tree/code.png",
          "valid_children": ["alpha", "tag"]
        }
      },
      'sort': function (a, b) {
        var type_a = this.get_type(a);
        var type_b = this.get_type(b);

        var a_folder = ['default', 'categorical'].indexOf(type_a) > -1;
        var b_folder = ['default', 'categorical'].indexOf(type_b) > -1;

        if ((type_a == 'tag') && (type_b != 'tag')) {
          return -1;
        } else if ((type_a != 'tag') && (type_b == 'tag')) {
          return 1;
        } else if (a_folder && !b_folder) {
          return -1;
        } else if (!a_folder && b_folder) {
          return 1;
        } else {
          return this.get_text(a) > this.get_text(b) ? 1 : -1;
        }
      },
      "plugins": ["dnd", "sort", "contextmenu", "types", "wholerow", "search"]
    });

function merge() {
    var options, name, src, copy, copyIsArray, clone, targetKey, target = arguments[0] || {}, i = 1, length = arguments.length, deep = false;
    var currentId = typeof arguments[length - 1] == 'string' ? arguments[length - 1] : null;
    if (currentId) {
        length = length - 1;
    }
    // Handle a deep copy situation
    if (typeof target === "boolean") {
        deep = target;
        target = arguments[1] || {};
        // skip the boolean and the target
        i = 2;
    }

    // Handle case when target is a string or something (possible in deep copy)
    if (typeof target !== "object" && !jQuery.isFunction(target)) {
        target = {};
    }

    // extend jQuery itself if only one argument is passed
    if (length === i) {
        target = this;
        --i;
    }

    for (; i < length; i++) {
        // Only deal with non-null/undefined values
        if ((options = arguments[i]) != null) {
            // Extend the base object
            for (name in options) {
                if (!options.hasOwnProperty(name)) {
                    continue;
                }
                copy = options[name];
                var mm = undefined;
                src = undefined;
                if (currentId && jQuery.isArray(options) && jQuery.isArray(target)) {
                    for (mm = 0; mm < target.length; mm++) {
                        if (currentId && (isSameString(target[mm][currentId], copy[currentId]))) {
                            src = target[mm];
                            break;
                        }
                    }
                }
                else {
                    src = target[name];
                }

                // Prevent never-ending loop
                if (target === copy) {
                    continue;
                }
                targetKey = mm !== undefined ? mm : name;
                // Recurse if we're merging plain objects or arrays
                if (deep && copy && (jQuery.isPlainObject(copy) || (copyIsArray = jQuery.isArray(copy)))) {
                    if (copyIsArray) {
                        copyIsArray = false;
                        clone = src && jQuery.isArray(src) ? src : [];

                    }
                    else {
                        clone = src && jQuery.isPlainObject(src) ? src : {};
                    }

                    // Never move original objects, clone them
                    if (currentId) {
                        target[targetKey] = merge(deep, clone, copy, currentId);
                    }
                    else {
                        target[targetKey] = merge(deep, clone, copy);
                    }

                    // Don't bring in undefined values
                }
                else if (copy !== undefined) {
                    target[targetKey] = copy;
                }
            }
        }
    }

    // Return the modified object
    return target;
}

function isSameString (a , b){
    return a && b && String(a).toLowerCase() === String(b).toLowerCase();
}

// Applying functions to buttons that can be selected in html dropdown
function applyTemplate (template) {
  console.log('Applying template.');
  var tree = $('#tree-div').jstree(true);
  var currentTreeState = tree.get_json('#');
  tree.settings.core.data = merge(true, currentTreeState, template, "text");
  tree.refresh();
}

var templateMap = {"button#fair-study-metadata" : {
                        path: "/static/templates/fair_study.metadata.json",
//                        name: "FAIR study level",
//                        category: "Metadata",
                        alertText: "Metadata template for FAIR metadata applied!",
                        },
                   "button#trait-master" : {
                        path: "/static/templates/trait_master_tree.template.json",
//                        name: "TraIT Master Tree",
//                        category: "Master",
                        alertText: "TraIT master template applied!",
                        }
                   };

for (var key in templateMap) {
  if (templateMap.hasOwnProperty(key)) {
    getTemplateCallback(key, templateMap[key].path, templateMap[key].alertText);
  }
}

function getTemplateCallback(button, filename, alertText) {
    return $(button).click( function () {
        console.log('Fetching: ' + filename);
        $.getJSON(filename, function(template) {
            applyTemplate(template);
        })
        .success( showAlert(alertText) )
        .error( console.log("Cannot apply, found an error in JSON.") );
    });
}

$(document).on('change', '.file-upload-button', function(event) {
  var reader = new FileReader();
  reader.onload = function(event) {
    var jsonObj = JSON.parse(event.target.result);
    applyTemplate(jsonObj);
    showAlert("Template applied from file.");
    // Reset button so it can be used again
    $('.file-upload-button').val("");
  };
  reader.readAsText(event.target.files[0]);
});

$("button#template-from-file").click( function ( ) {
  $('.file-upload-button').trigger('click');
});

function showAlert(text) {
    $('#alert-text').text(text);
    $("#myAlert").addClass("in");
    window.setTimeout(function () {
        $("#myAlert").removeClass("in");
    }, 4000);
}
$(document).ready(function(){
    $("#datalabel").keyup(function(){
        jstree.rename_node(node, $(this).val());
    });
});