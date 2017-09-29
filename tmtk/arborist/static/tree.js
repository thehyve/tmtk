var node, jstree, tagBuffer, ontologyTree;
var defaultTagWeight = 5;
var hasOntology = true;

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

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    $('button#embeded_return').bind('click', function () {
        $.ajax({
            method: "POST",
            contentType: "application/json",
            url: base_url + 'transmart-arborist',
            data: stringTree(),
            beforeSend: function(request) {
                return request.setRequestHeader("X-XSRFToken", getCookie('_xsrf'));
            }})
            .fail(function () {
                showAlert("Error encountered in saving column mapping file.", true);
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
        (key === 'type' && value === 'default')) {
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
        (key === 'type' && value !== 'tag') ||
        (key === 'children' && value.length === 0) ||
        (key === 'data' && !value.tags)) {
        return undefined;
    }
    return value;
}

// Button to check if tag table is filled and if so add new tag
function add_tags_feedback () {
    var empty = $('.tag-container div').filter(function() {
        return $(this).text() === "";
    });
    if (empty.length) {
        showAlert("Fill all fields to add new row.", true);
    } else {
        sortTags();
        // Add a new empty row
        createTagRow();
        // The popover has to be initialized
        activateTagPopover();
        // Select the newly added tag.
        $('.tag-container .trigger:last').click();
        $('.tag-title').focus();
        showAlert("Tags added.");
    }
}

function process_tags (obj) {
    // Reset tags object to clear all existing tags
    node.data.tags = {};

    $(".tag-container li").each(function(){

        var title = $(this).find('.list-tag-title').text();
        var desc = $(this).find('.list-tag-description').text();
        var weight = $(this).find('.list-tag-weight').text() || defaultTagWeight;

        console.log('Tag found: ' + title + ': ' + desc + ' (' + weight + ').');

        // If title and description are present, store it to the tags.
        if ( title !== "" && desc !== "" && typeof title !== "undefined" && typeof desc !=="undefined") {
            console.log('Adding tag.');
            node.data.tags[title] = [desc, weight];
        }
    });
    showAlert("Tags saved.")
}

$("button#tag-add").on('click', function () {
    add_tags_feedback();
});

$("button#tag-save").on('click', function () {
    process_tags();
    sortTags();
});

$("form#datanodedetails").submit(function (e) {
    e.preventDefault();
    var new_label = $("#datalabel").val();
    var updated = jstree.rename_node(node, new_label);

    if (node.type !== 'default'){

        if (typeof node.data === 'undefined') {
            node.data = {};
        }

        console.log($("#magic5").val(), $("#magic6").val());
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
            } else if ((node.type === 'codeleaf') && (!is_special)) {
                new_type = node.data['ctype'];
            }
            jstree.set_type(node, new_type);
            jstree.deselect_all();
            jstree.select_node(node);
        }
    }
});

function enableRightFields(type) {
    if ($.inArray(type, ['numeric', 'categorical', 'codeleaf', 'empty']) > -1) {
        $('.label').prop('hidden', false);
        $('.clinicaldata').prop('hidden', false);
        $('.metadata').prop('hidden', true);
        $('.hdtagdata').prop('hidden', true);
        $('.dfv').prop('hidden', true);
    } else if (type === 'tag') {
        console.log('Enable tags fields.');
        $('.metadata').prop('hidden', false);
        $('.clinicaldata').prop('hidden', true);
        $('.label').prop('hidden', true);
        $('.hdtagdata').prop('hidden', true);
        $('.dfv').prop('hidden', true);
    } else if (type === 'highdim') {
        console.log('Enable highdim fields.');
        $('.metadata').prop('hidden', true);
        $('.clinicaldata').prop('hidden', true);
        $('.hdtagdata').prop('hidden', false);
        $('.label').prop('hidden', false);
        $('.dfv').prop('hidden', true);
    } else {
        $('.label').prop('hidden', false);
        $('.metadata').prop('hidden', true);
        $('.hdtagdata').prop('hidden', true);
        $('.clinicaldata').prop('hidden', true);
        $('.dfv').prop('hidden', true);
    }
}

function customMenu(node) {
    $(".trigger").popover('hide'); // remove all existing popovers;
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
                        add_tags_feedback();
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
                tagNode = node.type === 'tag' ? node : jstree.get_node(node.children[0]);

                // if not tag child, create one.
                if (tagNode.type !== "tag") {
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
    if (node.type !== 'tag'){
        delete items.copyTags;
    } else {
        delete items.addTags;
    }
    if (!tagBuffer) {
        delete items.pasteTags;
    }
    return items;
}

function sortTags () {
    $('.tag-container > .trigger').sort(function (a, b) {

        var aEmpty = false;
        $(a).find('span').each(function() {
            if ($.trim($(this).html()) === '') {
                aEmpty = true;
            }
        });

        var bEmpty = false;
        $(b).find('span').each(function() {
            if ($.trim($(this).html()) === '') {
                bEmpty = true;
            }
        });

        if ( aEmpty ^ bEmpty ) { // XOR -> sink tags with empties to bottom.
            return aEmpty ? 1 : -1;
        }

        var weightA = parseInt($(a).children('.list-tag-weight').text());
        var weightB = parseInt($(b).children('.list-tag-weight').text());

        var weightsDiffer = (weightA < weightB) ? -1 : (weightA > weightB) ? 1 : 0;
        var textDiffer = (a.innerText < b.innerText) ? -1 : (a.innerText > b.innerText) ? 1 : 0;
        return weightsDiffer ? weightsDiffer : textDiffer;
    }).appendTo('.tag-container');
}

function createTagRow(){
    // Add new row to tags list and return it
    var tr = $('<li class="list-group-item trigger"></li>')
        .append('<button class="tag tag-danger tag-delete">del</button>')
        .append('<span class="tag tag-default list-group-item-number list-tag-weight">'+ defaultTagWeight +'</span>')
        .append('<div class="list-tag-row"><span class="list-group-item-heading list-tag-title"></div>')
        .append('<div class="list-tag-row"><span class="list-group-item-text list-tag-description"></span></div>');

    $(".tag-container").append(tr);
    return tr;
}

function activateTagPopover() {
    // Activate delete buttons
    $('.tag-delete').on('click', function() {
        var tagRow = $(this).closest(".trigger");
        tagRow.popover('hide'); // remove all existing popovers;
        tagRow.remove();
    });
    $('.trigger').popover({
        html: true,
        title: "Edit tag properties",
        content: function () {
            var title = $(this).find(".list-group-item-heading").text();
            var description = $(this).find(".list-group-item-text").text();
            var weight = $(this).find(".list-group-item-number").text() || defaultTagWeight;

            var form = $('<form></form>');
            form.append('<label>Title</label>');
            form.append('<input title="Title" type="text" class="form-control tag-title" value="' + title + '" />');
            form.append('<label>Description</label>');
            form.append('<textarea class="form-control tag-description">' + description + '</textarea>');
            form.append('<label>Weight</label>');
            form.append('<input type="number" class="form-control tag-weight" min="1" max="99" value=' + weight + ' />');
            return form;
        },
        constraints: [ { to: 'window', pin: true } ],
        placement: 'left'
    })
        .on('show.bs.popover', function () {
            $('.trigger').not(this).popover('hide'); //all but this
            $(this).addClass('active');
        })
        .on('hidden.bs.popover', function (e) {
            $(e.target).data("bs.popover")._activeTrigger.click = false;
            $(this).removeClass('active');
        })
        .on('shown.bs.popover', function () {
            var listItem = $(this);

            $('.popover-content').find(':input').on('keypress', function (e) {
                if ((e.keyCode || e.which) === 13) {
                    e.preventDefault();
                    if(event.shiftKey) {
                        $("button#tag-add").click();
                    } else {
                        $("button#tag-save").click();
                    }
                }
            });
            $(".tag-description").keyup(function (e) {
                listItem.find('.list-tag-description').text($(this).val());
            });
            $(".tag-title").keyup(function() {
                listItem.find('.list-tag-title').text($(this).val());
            });
            $(".tag-weight").on("change paste keyup", function() {
                var newWeight = ($(this).val() <= 99) ? $(this).val() : 99;
                newWeight = (newWeight >= 1) ? newWeight : 1;
                listItem.find('.list-tag-weight').text(newWeight);
                sortTags();
            });
        });
}

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
    $('#search-box').keyup(function () {
        var spinner = $("#search_spinner");
        spinner.show();
        var v = $('#search-box').val();
        if(to) { clearTimeout(to); }
        to = setTimeout(function () {
            jstree.search(v);
        }, 400);
        if(!v.length){
            spinner.hide();
        }
    });
});

// Create the main tree
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
        o = jstree.get_node(e.currentTarget);
        if (e.which === 46 || e.which === 8) {
            // remove node with forward or backward delete
            if (o === "#") {
                showAlert("Cannot remove root nodes.", true);
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
            if (node.type !== 'tag'){
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
    .on('click', function () {
        $(".trigger").popover('hide'); // remove all existing popovers;
    })
    .on('select_node.jstree', function (e, data) {
        $(".trigger").popover('hide'); // remove all existing popovers;
        node = data.instance.get_node(data.selected[0]);
        console.log('Node selected: ', node);

        $("form#datanodedetails")[0].reset();
        $("#datalabel").val(node.text);
        $("#nodetype").text(prettyType(node.type));

        enableRightFields(node.type);

        if (node.data !== null) {
            $("#filename").text(node.data['fn']);
            $("#columnnumber").text(node.data['col']);
            $("#datafile_header").text(node.data['dfh']);
            if (typeof node.data['m5'] !== 'undefined') {
                $("#magic5").val(node.data['m5']);
            }
            if (typeof node.data['m6'] !== 'undefined') {
                var cvcd = node.data['m6'];
                if (hasOntology && ontologyTree.get_node(cvcd)) {
                    ontologyTree.deselect_all();
                    ontologyTree.select_node(cvcd);
                }
                $("#magic6").val(cvcd);
            }
            if (node.data['cty'] === 'CATEGORICAL') {
                $("#fc").prop('checked', true);
            }
            if ((node.type === 'alpha') && (node.data['dfv'] !== node.text)) {
                $('.dfv').prop('hidden', false);
                $("#datafile_value").text(node.data['dfv']);
            }
            if ((node.type === 'highdim') && (node.data.hd_args !== 'undefined')) {
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
                $(".tag-container").empty();
                // Populate tags
                for (var key in node.data.tags) {
                    if (node.data.tags.hasOwnProperty(key)) {
                        var tagRow = createTagRow();

                        tagRow.find('.list-tag-title').text(key);
                        tagRow.find('.list-tag-description').text(node.data.tags[key][0]);
                        tagRow.find('.list-tag-weight').text(node.data.tags[key][1]);
                    }
                }
                sortTags();
                // The popover has to be initialized
                activateTagPopover();
            }
        }
    })
    // create the instance
    .jstree({
        'core': {
            'data': conceptTreeData,
            "check_callback": true
        },
        'dnd': {
            'is_draggable': function (node) {
                var previously_selected = jstree.get_selected();
                for (var i = 0; i < previously_selected.length; i++) {
                    var prev_node = jstree.get_node(previously_selected[i]);
                    if (prev_node.type === 'alpha') {
                        return false
                    }
                }
                return (node[0].type !== 'alpha');
            }
        },
        "unique": {case_sensitive : true},
        "contextmenu": {items: customMenu},

        "types": {
            "default": {
                "icon": static_base + "/images/tree/folder.gif"
            },
            "alpha": {
                "icon": static_base + "/images/tree/alpha.gif",
                "valid_children": ["tag"]
            },
            "categorical": {
                "icon": static_base + "/images/tree/folder.gif"
            },
            "numeric": {
                "icon": static_base + "/images/tree/numeric.gif",
                "valid_children": ["tag"]
            },
            "highdim": {
                "icon": static_base + "/images/tree/dna_icon.png",
                "valid_children": ["tag"]
            },
            "empty": {
                "icon": static_base + "/images/tree/empty.png"
            },
            "tag": {
                "icon": static_base + "/images/tree/tag_icon.png",
                "valid_children": "none"
            },
            "codeleaf": {
                "icon": static_base + "/images/tree/code.png",
                "valid_children": ["alpha", "tag"]
            }
        },
        'sort': function (a, b) {
            var type_a = this.get_type(a);
            var type_b = this.get_type(b);

            var a_folder = ['default', 'categorical'].indexOf(type_a) > -1;
            var b_folder = ['default', 'categorical'].indexOf(type_b) > -1;

            if ((type_a === 'tag') && (type_b !== 'tag')) {
                return -1;
            } else if ((type_a !== 'tag') && (type_b === 'tag')) {
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

$(function () {
    var to = false;
    $('#ontology-search').keyup(function () {
        var spinner = $("#ontology-search-spinner");
        spinner.show();
        var v = $('#ontology-search').val();
        if(to) { clearTimeout(to); }
        to = setTimeout(function () {
            ontologyTree.search(v);
        }, 400);
        if(!v.length){
            spinner.hide();
        }
    });
});


if (!ontologyTreeData.length) {
    console.log('No ontology tree found.');
    hasOntology = false;
    $('.ontology-tree-container').remove();
} else {
// Create the ontology tree
    $('#ontology-tree-div')
    // listen for event
        .on('loaded.jstree', function () {
            ontologyTree = $(this).jstree(true);
            $("#ontology-search-spinner").hide();
        })
        .on('search.jstree', function () {
            $("#ontology-search-spinner").hide();
        })
        .on('select_node.jstree', function (e, data) {

            var ontologyNode = data.instance.get_node(data.selected[0]);
            console.log('Ontology code selected: ', ontologyNode);

            $("#magic6").val(ontologyNode.data.code);

            $("#ontology-label").text(ontologyNode.text);
            $("#ontology-code")
                .attr('href', ontologyNode.data.uri)
                .text(ontologyNode.data.code);
        })
        // create the instance
        .jstree({
            'core': {
                'data': ontologyTreeData
            },
            'search': {
                'fuzzy': true
            },
            "types": {
                "default": {
                    "icon": static_base + "/images/tree/green_info.png"
                }
            },
            "plugins": ["types", "search"]
        });
}

function merge() {
    var options, name, src, copy, copyIsArray, clone, targetKey, target = arguments[0] || {}, i = 1, length = arguments.length, deep = false;
    var currentId = typeof arguments[length - 1] === 'string' ? arguments[length - 1] : null;
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
        if ((options = arguments[i]) !== null) {
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
    var currentTreeState = jstree.get_json('#');
    jstree.settings.core.data = merge(true, currentTreeState, template, "text");
    jstree.refresh();
}

var templateMap = {"button#fair-study-metadata" : {
                        path: static_base + "/templates/fair_study.metadata.json",
//                        name: "FAIR study level",
//                        category: "Metadata",
                        alertText: "Metadata template for FAIR metadata applied!"
                        },
                   "button#trait-master" : {
                        path: static_base + "/templates/trait_master_tree.template.json",
//                        name: "TraIT Master Tree",
//                        category: "Master",
                        alertText: "TraIT master template applied!"
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
            .success(function(){ showAlert(alertText)})
            .fail(function(jqXHR, textStatus, errorThrown) { console.log("Cannot apply, found an error in JSON: " + errorThrown)})
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

function showAlert(text, isWarning) {
    var alertColor = isWarning ? 'alert-warning' : 'alert-info';
    $('#alert-text').text(text);
    $("#myAlert").addClass("in " + alertColor);
    window.setTimeout(function () {
        $("#myAlert").removeClass("in " + alertColor);
    }, 4000);
}
$(document).ready(function(){
    $("#datalabel").keyup(function(){
        jstree.rename_node(node, $(this).val());
    });
    $("#bottom-btns").on('click', function() {
        $(".trigger").popover('hide'); // remove all existing popovers;
    });
});

function changeWeight(up) {
    var target = $('.tag-container .active').children('.list-tag-weight');
    if (target.length !== 1) {
        return undefined;
    }
    var increment = up ? 1 : -1;
    var newValue = parseInt(target.text() || defaultTagWeight) + increment || 1; // Don't go below 1
    newValue = (newValue <= 99) ? newValue : 99;
    target.text(newValue);
    $('.popover-content').find('.tag-weight').val(newValue);
    sortTags();
}

$(document).keydown(function(e) {
    switch(e.which) {

        case 38: // up
        changeWeight(false);
        break;

        case 40: // down
        changeWeight(true);
        break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});