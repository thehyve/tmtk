
// Add jstree json to the submit form as hidden parameter.
$("#edit_form").submit( function(eventObj) {
    var tree = stringTree();
    $('<input />').attr('type', 'hidden')
        .attr('name', 'json')
        .attr('id', 'id_json')
        .attr('value', tree)
        .appendTo('#edit_form');
    return true;
});

// use the download function to download a treefile with the name of the study. HTML5 stuff.
$('button#download').click( function (obj) {
    var tree = stringTree();
    serveDownload(study_name.toString() + '.treefile', tree)
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
    var v = $('#treediv').jstree(true).get_json('#', {'no_state': true});
    var tree = JSON.stringify(v, replacer);
    return tree;
}

// This function is used by JSON.stringify to exclude unnecessary nodes.
function replacer(key, value) {
    var skipped = ['icon', 'li_attr', 'a_attr'];
    if ($.inArray(key, skipped) > -1 |
            (key == 'type' & value == 'default')) {
        return undefined;
    }
    return value;
}

// Button to check if tag table is filled and if so add new tag
function add_tags_feedback (obj) {
    var empty = $('#tagtable-body').find("input").filter(function() {
        return this.value === "";
    });
    if (empty.length) {
        feedback("Fill all fields to add new row.", true);
    } else {
        createTagRow();
        feedback("Tags added.", false);
    }
};

function color_bg (id, color) {
    var item = document.getElementById(id)
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

    for (i = 1; i <= rowCount; i++) {
        var title = $("#tagname_" + i).val();
        var desc = $("#tagdesc_" + i).val();
        var weight = $("#tagweight_" + i).val();


        if (title === "" & desc !== "") {
            field_empty('tagname_' + i);
        } else if (desc === "" & title !== "") {
            field_empty('tagdesc_' + i);
        }

        var entry = old_tags[title];
        if (typeof entry !== 'undefined') {
            if ((desc !== "") & (entry[0] !== desc)){
                field_update("tagdesc_" + i);
            }
            if ((weight !== "") & (entry[1] !== weight)){
                field_update("tagweight_" + i);
            }
        } else if (title !== "" & desc !== "") {
            field_update("tagname_" + i);
            field_update("tagdesc_" + i);
            field_update("tagweight_" + i);
        }

        // If title and description are present, store it to the tags.
        if (title !== "" & desc !== "") {
            node.data.tags[title] = [desc, weight];
        }
    }
    add_tags_feedback()
}

$("form#datanodedetails").submit(function (e) {
  e.preventDefault();
  if (node.type == 'tag') {
    process_tags()
  } else if (typeof node != 'undefined') {

    var text = $("#datalabel").val();
    var updated = $("#treediv").jstree('rename_node', node, text);

    if (typeof node.data == 'undefined') {
      node.data = {}
    }

    node.data['m5'] = $("#magic5").val();
    node.data['m6'] = $("#magic6").val();

    if ($("#fc").prop('checked')) {
        node.data['cty'] = 'CATEGORICAL'
    } else {
        node.data['cty'] = ''
    }

    var type = node.type;

    if (updated) {
      feedback("Successfully applied", false);
      var is_special = ['SUBJ_ID', 'OMIT'].indexOf(text) > -1;

      // If the node text starts with OMIT, change the type (and icon)
      if (is_special & (['categorical', 'numeric', 'empty'].indexOf(type) > -1 )) {
        type = 'codeleaf';
      // If changed from SUBJ_ID or OMIT to regular, change type back to original
      } else if ((type == 'codeleaf') & (!is_special)) {
        type = node.data['ctype'];
      }

      $("#treediv").jstree('set_type', node, type);
      $("#treediv").jstree('deselect_all');
      $("#treediv").jstree('select_node', node);

    }
  } else {
    feedback("No node selected", true)
  }
});

function enableRightFields(type) {
  if (type == 'numeric' | type == 'categorical' | type == 'codeleaf' | type == 'empty' ) {
    $('.label').prop('hidden', false);
    $('.clinicaldata').prop('hidden', false);
    $('.tagdata').prop('hidden', true);
    $('.dfv').prop('hidden', true);
  } else if (type == 'tag') {
    $('.tagdata').prop('hidden', false);
    $('.clinicaldata').prop('hidden', true);
    $('.label').prop('hidden', true);
    $('.dfv').prop('hidden', true);
  } else {
    $('.label').prop('hidden', false);
    $('.tagdata').prop('hidden', true);
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
        var inst = $.jstree.reference(data.reference),
            obj = inst.get_node(data.reference);
        var tag_specs = {
          type: 'tag',
          text: 'Tags',
          data: { // This is added to prevent GUI error for Filename
            'fn': '',
            'tags': {},
          }
        }
        inst.create_node(obj, tag_specs, "last", function (new_node) {

          setTimeout(function () {
            inst.deselect_all();
            inst.select_node(new_node);
          }, 0);
        });
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

  return items;
}

function createTagRow(){
    // Add new row to tags table and return the row number
    var rowCount = $("#tagtable-body tr").length;
    var counter = rowCount + 1;

    var title_id = 'tagname_' + counter;
    var desc_id = 'tagdesc_' + counter;
    var weight_id = 'tagweight_' + counter;

    var some_style = ' class="form-control form-control-sm" style="width: 100%; "'

    var tdInput = '<input type="text" '+some_style+' placeholder="Title..." id="' + title_id + '" />';
    var tdDesc = '<input type="text" '+some_style+' placeholder="Description..." id="' + desc_id + '" />';
    var tdWeight = '<input type="number" class="form-control form-control-sm"  min="1" max="10" value="3" id="' + weight_id +'" />';

    var tr = $('<tr></tr>')
        .append('<td>'+tdInput+'</td>')
        .append('<td>'+tdDesc+'</td>')
        .append('<td>'+tdWeight+'</td>');

    $('#tagtable-body').append(tr);

    $('#' + title_id).focus()

    return counter
}

var keymap = {default : 'Folder',
              numeric : 'Numerical',
              alpha : 'Categorical Value',
              categorical : 'Categorical',
              tag : 'Metadata tags',
              highdim : 'High-dimensional',
              codeleaf : 'Special concept',
              empty: 'Empty node',
             };
function prettyType(label){
    return keymap[label]
}

$(function () {
  var to = false;
  $('#search_box').keyup(function () {
    $("#search_spinner").show();
    var v = $('#search_box').val();
    if(to) { clearTimeout(to); }
    to = setTimeout(function () {
      $('#treediv').jstree(true).search(v);
    }, 400);
    if(!v.length){
        $("#search_spinner").hide();
    }
  });
});

// Create the tree
$('#treediv')
// listen for event
    .on('loaded.jstree', function() {
      $("#search_spinner").hide();
      })
    .on('search.jstree', function() {
      $("#search_spinner").hide();
      })
    .on('select_node.jstree', function (e, data) {
      node = data.instance.get_node(data.selected[0]);
      $("form#datanodedetails")[0].reset();
      $("#datalabel").val(node.text);
      $("#nodetype").text(prettyType(node.type));

      enableRightFields(node.type);

      if (typeof node.data !== 'undefined') {
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

        // This way to add multiple tags to 'tags' dictionary in 'data'
        if (typeof node.data['tags'] !== 'undefined') {
          // Clear the existing tag table
          $('#tagtable-body').empty();
          // Populate tags
          for (var key in node.data.tags) {
            if (node.data.tags.hasOwnProperty(key)) {
                counter = createTagRow();

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
          if (node[0].type == 'alpha') {
            return false;
          }
          return true;
        }
      },
      "unique": {case_sensitive : true},
      "contextmenu": {items: customMenu},

      "types": {
        "default": {
          "icon": "/static/images/tree/folder.gif",
        },
        "alpha": {
          "icon": "/static/images/tree/alpha.gif",
          "valid_children": ["tag"]
        },
        "categorical": {
          "icon": "/static/images/tree/folder.gif",
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
          "icon": "/static/images/tree/empty.png",
        },
        "tag": {
          "icon": "/static/images/tree/tag_icon.png",
          "valid_children": "none"
        },
        "codeleaf": {
          "icon": "/static/images/tree/code.png",
          "valid_children": ["alpha", "tag"]
        },
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
