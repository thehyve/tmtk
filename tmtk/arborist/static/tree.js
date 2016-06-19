
// Add jstree json to the submit form as hidden parameter.
$("#edit_form").submit( function(eventObj) {
    var v = $('#treediv').jstree(true).get_json()
    var tree = JSON.stringify(v);
    $('<input />').attr('type', 'hidden')
        .attr('name', 'json')
        .attr('id', 'id_json')
        .attr('value', tree)
        .appendTo('#edit_form');
    return true;
});

// use the download function to download a treefile with the name of the study. HTML5 stuff.
$('button#download').click( function (obj) {
    var v = $('#treediv').jstree(true).get_json()
    var tree = JSON.stringify(v);
    download(study_name.toString() + '.treefile', tree)
});

function download(filename, text) {
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
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

var node;

// Keep this for the embedded return from Jupyter Notebooks
$(function () {
  $('button#embeded_return').bind('click', function () {
    var v = $('#treediv').jstree(true).get_json()
    var tree = JSON.stringify(v);

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

var node;

$("form#datanodedetails").submit(function (e) {
  e.preventDefault();
  if (node.type == 'tag') {

    for (i = 1; i < 5; i++) {
      var title = $("input[name='tag_tit" + i + "']").val();
      var desc = $("input[name='tag_desc" + i + "']").val();
      var weight = $("input[name='tag_weight" + i + "']").val();
      node.data.tags[title] = [desc, weight]
    }
  } else if (typeof node != 'undefined') {

    var text = $("input[name='datalabel']").val();
    var updated = $("#treediv").jstree('rename_node', node, text);
    var type = $("select[name='nodetype']").val();
    $("#treediv").jstree('set_type', node, type);
    enableRightFields(type);

    if (typeof node.data == 'undefined') {
      node.data = {}
    }

    node.data['Filename'] = $("input[name='filename']").val();
    node.data['Column Number'] = $("input[name='columnnumber']").val();
    node.data['Data Label Source'] = $("input[name='datalabelsource']").val();
    node.data['Control Vocab Cd'] = $("input[name='controlvocabcd']").val();
    if (updated) {
      feedback("Successfully applied", false)
    }
  } else {
    feedback("No node selected", true)
  }
});

function enableRightFields(type) {
  if (type == 'numeric' | type == 'categorical') {
    $('.label').prop('hidden', false);
    $('.clinicaldata').prop('hidden', false);
    $('.tagdata').prop('hidden', true);
  } else if (type == 'tag') {
    $('.tagdata').prop('hidden', false);
    $('.clinicaldata').prop('hidden', true);
    $('.label').prop('hidden', true);
  } else {
    $('.label').prop('hidden', false);
    $('.tagdata').prop('hidden', true);
    $('.clinicaldata').prop('hidden', true);
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
            'Filename': '',
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
    renameItem: { // The "rename" menu item
      label: "Rename",
      action: function (data) {
        var inst = $.jstree.reference(data.reference),
            obj = inst.get_node(data.reference);
        inst.edit(obj);
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

  /* // Select here what options to show for which nodes to show what options.
   if (node.data.file) {
   delete items.createItem;
   }

   else{
   delete items.deleteItem;
   delete items.renameItem;
   }
   */
  return items;
}


// Create the tree
$('#treediv')
// listen for event
    .on('select_node.jstree', function (e, data) {
      node = data.instance.get_node(data.selected[0]);
      $("form#datanodedetails")[0].reset();
      $("input[name='datalabel']").val(node.text);
      $("select[name='nodetype']").val(node.type);

      enableRightFields(node.type);

      if (typeof node.data !== 'undefined') {
        $("input[name='filename']").val(node.data['Filename']);
        $("input[name='columnnumber']").val(node.data['Column Number']);
        if (typeof node.data['Data Label Source'] !== 'undefined') {
          $("input[name='datalabelsource']").val(node.data['Data Label Source']);
        }
        if (typeof node.data['Control Vocab Cd'] !== 'undefined') {
          $("input[name='controlvocabcd']").val(node.data['Control Vocab Cd']);
        }

        // This (ugly) way to add multiple tags to 'tags' dictionary in 'data'
        if (typeof node.data['tags'] !== 'undefined') {

          var counter = 0;

          for (var key in node.data.tags) {
            if (node.data.tags.hasOwnProperty(key)) {
              counter++
              var c = counter.toString()
              var tit = '[name="' + 'tag_tit' + c + '"]'
              var desc = '[name="' + 'tag_desc' + c + '"]'
              var weight = '[name="' + 'tag_weight' + c + '"]'
              $(tit).val(key);
              $(desc).val(node.data.tags[key][0]);
              $(weight).val(node.data.tags[key][1]);

            }
          }
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
      "contextmenu": {items: customMenu},

      "types": {
        "default": {
          "icon": "/static/images/tree/folder.gif",
          "valid_children": ["alpha",
            "numeric",
            "highdim",
            "codeleaf",
            "default",
            "categorical",
            "tag"]
        },
        "study": {
          "icon": "/static/images/tree/study.png",
          "valid_children": "all"
        },
        "alpha": {
          "icon": "/static/images/tree/alpha.gif",
          "valid_children": ["tag"]
        },
        "categorical": {
          "max_depth": "2",
          "icon": "/static/images/tree/folder.gif",
          "valid_children": ["alpha", "tag"]
        },
        "numeric": {
          "icon": "/static/images/tree/numeric.gif",
          "valid_children": ["tag"]
        },
        "highdim": {
          "icon": "/static/images/tree/dna_icon.png",
          "valid_children": ["tag"]
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
        if ((this.get_type(a) == 'tag') && (this.get_type(b) != 'tag')) {
          return -1;
        } else if ((this.get_type(a) != 'tag') && (this.get_type(b) == 'tag')) {
          return 1;
        } else if ((this.get_type(a) == 'default') && (this.get_type(b) != 'default')) {
          return -1;
        } else if ((this.get_type(a) != 'default') && (this.get_type(b) == 'default')) {
          return 1;
        } else {
          return this.get_text(a) > this.get_text(b) ? 1 : -1;
        }
      },
      "plugins": ["dnd", "sort", "contextmenu", "types", "unique", "wholerow"]
    });
