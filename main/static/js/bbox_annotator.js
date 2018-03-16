// Generated by CoffeeScript 2.2.2
(function() {
  // Use coffee-script compiler to obtain a javascript file.

  //    coffee -c bbox_annotator.coffee

  // See http://coffeescript.org/

  // BBox selection window.

  var BBoxSelector;

  BBoxSelector = class BBoxSelector {
    // Initializes selector in the image frame.
    constructor(image_frame, options) {
      if (options == null) {
        options = {};
      }
      options.input_method || (options.input_method = "text");
      this.update_pointer = true;
      this.move = false;
      this.start_from_scratch = true;
      this.image_frame = image_frame;
      this.border_width = options.border_width || 4;
      this.selector = $('<div class="bbox_selector"></div>');
      this.selector.css({
        "border": this.border_width + "px dotted rgb(255,30,30)",
        "position": "absolute"
      });
      this.image_frame.append(this.selector);
      this.selector.css({
        "border-width": this.border_width
      });
      this.selector.hide();
      this.create_label_box(options);
    }

    // Initializes a label input box.
    create_label_box(options) {
      var i, label, len, ref;
      options.labels || (options.labels = ["object"]);
      this.label_box = $('<div class="label_box"></div>');
      this.label_box.css({
        "position": "absolute"
      });
      this.image_frame.append(this.label_box);
      switch (options.input_method) {
        case 'select':
          if (typeof options.labels === "string") {
            options.labels = [options.labels];
          }
          this.label_input = $('<select class="label_input" name="label"></select>');
          this.label_box.append(this.label_input);
          this.label_input.append($('<option value>choose an item</option>'));
          ref = options.labels;
          for (i = 0, len = ref.length; i < len; i++) {
            label = ref[i];
            this.label_input.append('<option value="' + label + '">' + label + '</option>');
          }
          this.label_input.change(function(e) {
            return this.blur();
          });
          break;
        case 'text':
          if (typeof options.labels === "string") {
            options.labels = [options.labels];
          }
	  this.label_input = $('<input class="label_input" placeholder="Type object name... (choose one from suggestions)" size="50%" name="label" ' + 'type="text" value>');
          this.label_box.append(this.label_input);
          this.label_input.autocomplete({
            source: options.labels || [''],
            autoFocus: true,
            select: function( event, ui ) {
              this.value = ui.item.label;
              this.blur();
              return false;
            }
          });
          break;
        case 'fixed':
          if ($.isArray(options.labels)) {
            options.labels = options.labels[0];
          }
          this.label_input = $('<input class="label_input" name="label" type="text">');
          this.label_box.append(this.label_input);
          this.label_input.val(options.labels);
          break;
        default:
          throw 'Invalid label_input parameter: ' + options.input_method;
      }
      return this.label_box.hide();
    }

    // Crop x and y to the image size.
    crop(pageX, pageY) {
      var point;
      return point = {
        x: Math.min(Math.max(Math.round(pageX - this.image_frame.offset().left), 0), Math.round(this.image_frame.width() - 1)),
        y: Math.min(Math.max(Math.round(pageY - this.image_frame.offset().top), 0), Math.round(this.image_frame.height() - 1))
      };
    }

    // When a new selection is made.
    start(pageX, pageY) {
      this.start_from_scratch = true;
      this.update_pointer = true;
      this.move = false;
      this.pointer = this.crop(pageX, pageY);
      this.offset = this.pointer;
      this.refresh();
      this.selector.show();
      $('body').css('cursor', 'crosshair');
      return document.onselectstart = function() {
        return false;
      };
    }

    start_with_existing(entry, update_pointer, move) {
      this.start_from_scratch = false;
      this.update_pointer = update_pointer;
      this.move = move;
    //  TODO use existing label
      this.offset = {x: entry.left, y: entry.top};
      this.pointer = {x: entry.left + entry.width, y: entry.top + entry.height};
      this.label_input.val(entry.label);
      this.label_input.attr("label", entry.label);
      this.refresh();
      this.selector.show();
      $('body').css('cursor', 'crosshair');
      return document.onselectstart = function() {
        return false;
      };
    }

    // When a selection updates.
    update_rectangle(pageX, pageY) {
      // console.log("this.update_pointer: " + this.update_pointer);
      if (this.move) {
        var width = this.pointer.x - this.offset.x;
        var height = this.pointer.y - this.offset.y;
        this.offset = this.crop(pageX, pageY);
        this.offset.x -= width*0.5;
        this.pointer = this.crop(pageX, pageY);
        this.pointer.x += width*0.5;
        this.pointer.y += height;
      } else {
        if (this.update_pointer) {
          this.pointer = this.crop(pageX, pageY);
        } else {
          this.offset = this.crop(pageX, pageY);
        }
      }
      return this.refresh();
    }

    // When starting to input label.
    input_label(options) {
      $('body').css('cursor', 'default');
      document.onselectstart = function() {
        return true;
      };
      this.label_box.show();
      return this.label_input.focus();
    }

    // Finish and return the annotation.
    finish(options) {
      var data;
      this.label_box.hide();
      this.selector.hide();
      data = this.rectangle();
      var label  = this.label_input.val();
      if (!label) {
        label = this.label_input.attr('label');
      }
      // if the user didn't select one option, label is null
      if (label) {
        data.label = $.trim(label.toLowerCase());
      }
      if (options.input_method !== 'fixed') {
        this.label_input.val('');
      }
      return data;
    }

    // Get a rectangle.
    rectangle() {
      var rect, x1, x2, y1, y2;
      x1 = Math.min(this.offset.x, this.pointer.x);
      y1 = Math.min(this.offset.y, this.pointer.y);
      x2 = Math.max(this.offset.x, this.pointer.x);
      y2 = Math.max(this.offset.y, this.pointer.y);
      return rect = {
        left: x1,
        top: y1,
        width: x2 - x1 + 1,
        height: y2 - y1 + 1
      };
    }

    // Update css of the box.
    refresh() {
      var rect;
      rect = this.rectangle();
      this.selector.css({
        left: (rect.left - this.border_width) + 'px',
        top: (rect.top - this.border_width) + 'px',
        width: rect.width + 'px',
        height: rect.height + 'px'
      });
      return this.label_box.css({
        left: (rect.left - this.border_width) + rect.width - this.label_box.width() + 'px',
        top: (rect.top + rect.height + this.border_width) + 'px'
      });
    }

    // Return input element.
    get_input_element() {
      return this.label_input;
    }

  };

  // Annotator object definition.
  this.BBoxAnnotator = class BBoxAnnotator {
    // Initialize the annotator layout and events.
    constructor(options) {
      this.status = 'free';
      var annotator, image_element;
      annotator = this;
      this.annotator_element = $(options.id || "#bbox_annotator");
      this.border_width = options.border_width || 4;
      this.show_label = options.show_label || (options.input_method !== "fixed");
      this.image_frame = $('<div class="image_frame"></div>');
      this.annotator_element.append(this.image_frame);
      image_element = new Image();
      image_element.src = options.url;
      image_element.onload = function() {
        options.width || (options.width = image_element.width);
        options.height || (options.height = image_element.height);
        annotator.annotator_element.css({
          "width": (options.width + annotator.border_width * 2) + 'px',
          "height": (options.height + annotator.border_width * 2) + 'px',
          "cursor": "crosshair"
        });
        annotator.image_frame.css({
          "background-image": "url('" + image_element.src + "')",
          "width": options.width + "px",
          "height": options.height + "px",
          "position": "relative"
        });
        annotator.selector = new BBoxSelector(annotator.image_frame, options);
        return annotator.initialize_events(annotator.selector, options);
      };
      image_element.onerror = function() {
        return annotator.annotator_element.text("Invalid image URL: " + options.url);
      };
      this.entries = [];
      this.onchange = options.onchange;
    }

    // Initialize events.
    initialize_events(selector, options) {
      var annotator;
      this.hit_menuitem = false;
      annotator = this;
      annotator.status = 'free';
      this.annotator_element.mousedown(function(e) {
        if (!annotator.hit_menuitem) {
          switch (annotator.status) {
            case 'free':
            case 'input':
              if (annotator.status === 'input') {
                selector.get_input_element().blur();
              }
              if (e.which === 1) { // left button
                selector.start(e.pageX, e.pageY);
                annotator.status = 'hold';
              }
          }
        }
        annotator.hit_menuitem = false;
        return true;
      });
      $(window).mousemove(function(e) {
        switch (annotator.status) {
          case 'hold':
            selector.update_rectangle(e.pageX, e.pageY);
        }
        return true;
      });
      $(window).mouseup(function(e) {
        switch (annotator.status) {
          case 'hold':
            selector.update_rectangle(e.pageX, e.pageY);
            if (selector.start_from_scratch) {
              selector.input_label(options);
              annotator.status = 'input';
              if (options.input_method === 'fixed') {
                selector.get_input_element().blur();
              }
            } else {
              annotator.status = 'input';
              selector.get_input_element().blur();
            }

        }
        annotator.hit_menuitem = false;
        //annotator.status = 'free';
        return true;
      });
      selector.get_input_element().blur(function(e) {
        var data;
        switch (annotator.status) {
          case 'input':
            data = selector.finish(options);
            if (data.label) {
            // if (options.labels.includes(data.label)) {
              annotator.add_entry(data);
              if (annotator.onchange) {
                annotator.onchange(annotator.entries);
              }
            }
            // else {
            //   alert("invalid object: " + data.label);
            // }
            annotator.status = 'free';
        }
        return true;
      });
      selector.get_input_element().keypress(function(e) {
        switch (annotator.status) {
          case 'input':
            if (e.which === 13) {
              selector.get_input_element().blur();
            }
        }
        return e.which !== 13;
      });

      selector.get_input_element().mousedown(function(e) {
        return annotator.hit_menuitem = true;
      });
      selector.get_input_element().mousemove(function(e) {
        return annotator.hit_menuitem = true;
      });
      selector.get_input_element().mouseup(function(e) {
        return annotator.hit_menuitem = true;
      });
      return selector.get_input_element().parent().mousedown(function(e) {
        return annotator.hit_menuitem = true;
      });
    }

    // Add a new entry.
    add_entry(entry) {
      if (entry.width * entry.height < 600) {
      	entry.width = Math.max(20, entry.width);
      	entry.height = Math.max(30, entry.height);
      }
      var annotator, box_element, close_button, se_resize_button, nw_resize_button, move_button, text_box;
      this.entries.push(entry);
      box_element = $('<div class="annotated_bounding_box"></div>');
      // box_element.appendTo(this.image_frame).css({
      box_element.css({
        "border": this.border_width + "px solid rgb( 255, 87, 51)",
        "position": "absolute",
        "top": (entry.top - this.border_width) + "px",
        "left": (entry.left - this.border_width) + "px",
        "width": entry.width + "px",
        "height": entry.height + "px",
        "color": "rgb( 255, 87, 51)",
        "font-size": "small",
        "pointer-events":"none"
      });
      // this.image_frame.prepend(box_element);
      box_element.appendTo(this.image_frame);
      close_button = $('<div class="fa fa-times-circle"></div>').appendTo(box_element).css({
        "position": "absolute",
        "top": "-10px",
        "right": "-12px",
        "width": "16px",
        "height": "16px",
        "overflow": "hidden",
        "color": "#000",
        "cursor": "pointer",
        "-moz-user-select": "none",
        "user-select": "none",
        "text-align": "center",
        "pointer-events":"auto"
      });
      se_resize_button = $('<div name="se_resize_button"></div>').appendTo(box_element).css({
        "position": "absolute",
        "bottom": "-8px",
        "right": "-5px",
        "width": "16px",
        "height": "16px",
        "overflow": "hidden",
        "color": "#000",
        "cursor": "se-resize",
        "-moz-user-select": "none",
        "-webkit-user-select": "none",
        "user-select": "none",
        "text-align": "center",
        "pointer-events":"auto"
      });
      $("<div></div>").appendTo(se_resize_button).html('&#8690').css({
        "display": "block",
        "text-align": "center",
        "width": "16px",
        "position": "absolute",
        // "top": "-2px",
        // "left": "0",
        "font-weight": "bold",
        "font-size": "16px",
        "line-height": "16px",
        "font-family": '"Helvetica Neue", Consolas, Verdana, Tahoma, Calibri, ' + 'Helvetica, Menlo, "Droid Sans", sans-serif'
      });

      nw_resize_button = $('<div name="nw_resize_button"></div>').appendTo(box_element).css({
        "position": "absolute",
        "top": "-3px",
        "left": "-4px",
        "width": "16px",
        "height": "16px",
        "overflow": "hidden",
        "color": "#000",
         // "background-color": "#ccc",
        "cursor": "nw-resize",
        "-moz-user-select": "none",
        "-webkit-user-select": "none",
        "user-select": "none",
        "text-align": "center",
        "pointer-events":"auto"
      });

      $("<div></div>").appendTo(nw_resize_button).html('&#8689').css({
        "display": "block",
        "text-align": "center",
        "width": "16px",
        "position": "absolute",
        // "top": "-2px",
        // "left": "0",
        "font-weight": "bold",
        "font-size": "16px",
        "line-height": "16px",
        "font-family": '"Helvetica Neue", Consolas, Verdana, Tahoma, Calibri, ' + 'Helvetica, Menlo, "Droid Sans", sans-serif'
      });

      move_button = $('<div class="fa fa-plus-circle" name="move_button"></div>').appendTo(box_element).css({
        "position": "absolute",
        "top": "-10px",
        "left": entry.width*0.5 - 12 + "px",
        "width": "16px",
        "height": "16px",
        // "padding": "16px 0 0 0",
        "overflow": "hidden",
        "color": "#000",
        // "background-color": "#030",
        // "border": "2px solid #fff",
        // "-moz-border-radius": "18px",
        // "-webkit-border-radius": "18px",
        // "border-radius": "18px",
        "cursor": "move",
        "-moz-user-select": "none",
        // "-webkit-user-select": "none",
        "user-select": "none",
        "text-align": "center",
        "pointer-events":"auto"
      });

      text_box = $('<div></div>').appendTo(box_element).css({
        "position": "absolute",
        "top": "2px",
        "left": "15px",
        "overflow": "hidden"
      });
      if (this.show_label) {
        text_box.text(entry.label);
      }
      annotator = this;
      // box_element.hover((function(e) {
      //   return close_button.show();
      // }), (function(e) {
      //   return close_button.hide();
      // }));

      //[move_button, nw_resize_button, se_resize_button].forEach(function (t) {
      //  t.hover((function (e) {
      //    t.fadeTo(1, 1);
      //  }), (function (e) {
      //    t.fadeTo(1, 0.06);
      //  }));
      //});

      [move_button, nw_resize_button, se_resize_button].forEach(function (t) {
        t.hover((function(e) {
          if (annotator.status !== 'hold') {
            return annotator.hit_menuitem = true;
          }
        }), (function(e) {
          return annotator.hit_menuitem = false;
        }));
        t.mousemove(function (e) {
          if (annotator.status !== 'hold' && annotator.status !== 'focused' && annotator.status !== 'input') {
            annotator.hit_menuitem = false;
            annotator.status = 'free';
          }
        });
        t.mouseup(function (e) {
          if (annotator.status !== 'hold') {
            annotator.hit_menuitem = false;
            annotator.status = 'free';
          }
        });
        t.mousedown(function(e) {
          // return annotator.hit_menuitem = true;
          if (annotator.status !== "hold") {
            annotator.hit_menuitem = true;
            var clicked_box, index;
            clicked_box = se_resize_button.parent(".annotated_bounding_box");
            index = clicked_box.prevAll(".annotated_bounding_box").length;
            clicked_box.detach();
            entry = annotator.entries.splice(index, 1)[0];
            if (t.attr("name") === "se_resize_button")
              annotator.selector.start_with_existing(entry, true, false);
            if (t.attr("name") === "nw_resize_button")
              annotator.selector.start_with_existing(entry, false, false);
            if (t.attr("name") === "move_button")
              annotator.selector.start_with_existing(entry, false, true);
            annotator.status = 'hold';
          }
        });

      });


      close_button.mousedown(function(e) {
        return annotator.hit_menuitem = true;
      });

      close_button.click(function(e) {
        var clicked_box, index;
        clicked_box = close_button.parent(".annotated_bounding_box");
        index = clicked_box.prevAll(".annotated_bounding_box").length;
        clicked_box.detach();
        annotator.entries.splice(index, 1);
        return annotator.onchange(annotator.entries);
      });
      //[move_button, nw_resize_button, se_resize_button].forEach(function (t) { t.fadeTo(800,0.06); });
      // return close_button.hide();
    }

    // Clear all entries.
    clear_all(e) {
      this.annotator_element.find(".annotated_bounding_box").detach();
      this.entries.splice(0);
      return this.onchange(this.entries);
    }

    update_labels(labels) {
      var label_input = this.selector.get_input_element();
      label_input.empty();
      for (var i = 0; i < labels.length; i++) {
        var label = labels[i];
        label_input.append('<option value="' + label + '">' + label + '</option>');
      }
      label_input.attr("size", labels.length);
    }

  };

}).call(this);
