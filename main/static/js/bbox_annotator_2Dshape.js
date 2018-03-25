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
        // "border": this.border_width + "px solid rgb(255,30,30)",
        "position": "absolute",
        "background-color": "rgba(100,100,100, 0.5)"
      });
      this.image_frame.append(this.selector);
      this.selector.css({
        "border-width": this.border_width
      });
      this.selector.hide();
      this.create_label_box(options);
      this.shape = '';
    }

    set_shape(shape) {
      this.shape = shape;
    }

    // Initializes a label input box.
    create_label_box(options) {
      var i, label, len, ref;
      options.labels || (options.labels = ["red", "green", "blue"]);
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
          this.label_input = $('<select class="label_input" name="label" size="3"></select>');
          this.label_box.append(this.label_input);
          // this.label_input.append($('<option value>choose an item</option>'));
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

    // // When a new selection is made.
    // start(pageX, pageY) {
    //   this.start_from_scratch = true;
    //   this.update_pointer = true;
    //   this.move = false;
    //   this.pointer = this.crop(pageX, pageY);
    //   this.offset = this.pointer;
    //   this.refresh();
    //   this.selector.show();
    //   $('body').css('cursor', 'crosshair');
    //   return document.onselectstart = function() {
    //     return false;
    //   };
    // }

    start_with_existing(entry, update_pointer, move, pageX, pageY) {
      this.start_from_scratch = false;
      this.update_pointer = update_pointer;
      this.move = move;
      this.mouse_start = this.crop(pageX, pageY);
      this.shape = entry.shape;
    //  TODO use existing label
      this.offset = {x: entry.left, y: entry.top};
      this.pointer = {x: entry.left + entry.width, y: entry.top + entry.height};
      this.label_input.val(entry.label);
      this.label_input.attr("label", entry.label);
      this.refresh();
      this.selector.show();
      // $('body').css('cursor', 'crosshair');
      return document.onselectstart = function() {
        return false;
      };
    }

    // When a selection updates.
    update_rectangle(pageX, pageY) {
      if (this.move) {
        var mouse = this.crop(pageX, pageY);
        var offsetx = mouse.x - this.mouse_start.x;
        var offsety = mouse.y - this.mouse_start.y;
        this.mouse_start = mouse;
        this.offset.x += offsetx;
        this.offset.y += offsety;
        this.pointer.x += offsetx;
        this.pointer.y += offsety;
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
      data.shape = this.shape;
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
      if (!this.update_pointer) {
        // var size = Math.max(x2 - x1 + 1, y2 - y1 + 1);
        var size = Math.max(x2 - x1, y2 - y1);
        return rect = {
        left: x2 - size,
        top: y2 - size,
        width: size,
        height: size
      };
      } else {
      return rect = {
        left: x1,
        top: y1,
        width: Math.max(x2 - x1, y2 - y1),
        height: Math.max(y2 - y1, x2 - x1)
      };
      }


      // return rect = {
      //   left: x1,
      //   top: y1,
      //   width: Math.max(x2 - x1 + 1, y2 - y1 + 1),
      //   height: Math.max(y2 - y1 + 1, x2 - x1 + 1)
      // };
    }

    // Update css of the box.
    refresh() {
      var rect;
      rect = this.rectangle();
      if (this.shape === "rectangle") {
        this.selector.css({
          "border-radius": "",
          left: (rect.left) + 'px',
          top: (rect.top) + 'px',
          width: rect.width + 'px',
          height: rect.height + 'px',
          "border-left": '0px',
          "border-right": '0px',
          "border-bottom": '0px',
          "background-color": "rgba(100,100,100, 0.5)"
        });
      } else if (this.shape === "circle") {
        this.selector.css({
          "border-radius": "50%",
          left: (rect.left) + 'px',
          top: (rect.top) + 'px',
          width: rect.width + 'px',
          height: rect.height + 'px',
          "border-left": '0px',
          "border-right": '0px',
          "border-bottom": '0px',
          "background-color": "rgba(100,100,100, 0.5)"
        });
      } else if (this.shape === "triangle") {
        this.selector.css({
          "border-radius": "",
          left: (rect.left) + 'px',
          top: (rect.top) + 'px',
          "border-left": (rect.width / 2) + 'px solid transparent',
          "border-right": (rect.width / 2) + 'px solid transparent',
          "border-bottom": (rect.height) + "px solid rgba(100,100,100, 0.5)",
          "background-color": "",
          width: '0px',
          height: '0px'
        });
      } else {
        alert("unkown shape");
      }
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
      this.top_element = $("#bbox_annotator");
      var shapes = $('<div></div>');
      this.rectangle = $('<button id="input_rectangle" value="rectangle"> square &#9632;</button>');
      this.circle = $('<button id="input_circle" value="circle"> circle &#9679;</button>');
      this.triangle = $('<button id="input_triangle" value="triangle"> triangle &#9650;</button>');
      this.input_shape = '';

      // [rectangle, circle, triangle].forEach(function (t) {
      //   this.annotator_element.append(t);
      // });
      shapes.append(this.rectangle);
      shapes.append(this.circle);
      shapes.append(this.triangle);

      this.top_element.append(shapes);

      this.annotator_element = $('<div id="bbox_annotator_inner" style="display:inline-block"></div>');
      this.top_element.append(this.annotator_element);
      // this.element.append(this.annotator_element);
      this.border_width = options.border_width || 4;
      // this.show_label = options.show_label || (options.input_method !== "fixed");
      this.show_label = false;
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
          // "cursor": "crosshair"
        });
        annotator.image_frame.css({
          "background-image": "url('" + image_element.src + "')",
          "width": "500px",
          "height": "500px",
          "position": "relative"
        });

        // add 5x6 grid
        this.grid_blocks = [];
        var grid_size = 100;
        for (var row = 0; row < 5; ++row) {
          for (var col = 0; col < 5; ++col) {
            var grid_block = $('<div class="grid_block"></div>');
            grid_block.attr("x", col*grid_size);
            grid_block.attr("y", row*grid_size);
            grid_block.attr("width", grid_size);
            grid_block.attr("height", grid_size);
            this.grid_blocks.push(grid_block);
            grid_block.appendTo(annotator.image_frame).css({
                "opacity": 0.5,
                "border": "1px dotted gray",
                "position": "absolute",
                "top": row * grid_size + "px",
                "left": col * grid_size + "px",
                "width": grid_size + "px",
                "height": grid_size + "px",
                "pointer-events": "auto"
              });
          }
        }
        annotator.selector = new BBoxSelector(annotator.image_frame, options);
        annotator.initialize_events(annotator.selector, options, this.grid_blocks);
        this.grid_blocks.forEach(function (t) {
          t.hover((function (e) {
            if (annotator.input_shape && annotator.status !== 'hold') {
              $(this).css("background-color", "gray");
            }
          }), (function (e) {
            $(this).css("background-color", "");
          }));
        });

        this.grid_blocks.forEach(function (t) {
          t.click(function (e) {
            if (annotator.input_shape && !annotator.hit_menuitem) {
              annotator.selector.offset = {x: parseInt(t.attr('x')) + 10, y: parseInt(t.attr('y')) + 10};
              annotator.selector.pointer = {
                x: parseInt(t.attr('x')) + parseInt(t.attr('width')) - 10,
                y: parseInt(t.attr('y')) + parseInt(t.attr('height') - 10)
              };
              // this will also update position of label_box
              annotator.selector.refresh();
              annotator.selector.selector.show();
              annotator.status = 'input';
              var pointer = annotator.selector.crop(e.pageX, e.pageY);
              annotator.selector.label_box.css({
                left: pointer.x + 'px',
                top: pointer.y + 'px'
              });
              annotator.selector.label_box.show();
              annotator.selector.label_input.focus();
            }
          });
        });
      };
      image_element.onerror = function() {
        return annotator.annotator_element.text("Invalid image URL: " + options.url);
      };
      this.entries = [];
      this.onchange = options.onchange;
    }

    // Initialize events.
    initialize_events(selector, options, grid_blocks) {
      var annotator;
      this.hit_menuitem = false;
      annotator = this;
      annotator.status = 'free';
      [annotator.rectangle, annotator.circle, annotator.triangle].forEach(function (t) {
        t.click(function () {
          if (annotator.input_shape !== $( this ).val()) {
            annotator.input_shape = $(this).val();
            selector.set_shape(annotator.input_shape);
            annotator.annotator_element.css('cursor', 'pointer');

            ['rectangle', 'circle', 'triangle'].forEach(function (t2) {
              if (t2 === annotator.input_shape) {
                $('#input_' + t2).css('font-weight', '900');
              } else {
                $('#input_' + t2).css('font-weight', '');
              }
            });
          }
        });
      });
      // this.annotator_element.mousedown(function(e) {
      //   if (!annotator.hit_menuitem && annotator.input_shape) {
      //     switch (annotator.status) {
      //       case 'free':
      //       case 'input':
      //         if (annotator.status === 'input') {
      //           selector.get_input_element().blur();
      //         }
      //         if (e.which === 1) { // left button
      //           selector.start(e.pageX, e.pageY);
      //           annotator.status = 'hold';
      //         }
      //     }
      //   }
      //   annotator.hit_menuitem = false;
      //   return true;
      // });
      $(window).mousemove(function(e) {
        switch (annotator.status) {
          case 'hold':
            selector.update_rectangle(e.pageX, e.pageY);
            if (selector.move) {
              annotator.annotator_element.css('cursor', 'move');
            }
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
              var p = selector.crop(e.pageX, e.pageY);
              for (var i = 0; i < grid_blocks.length; i++) {
                var t = grid_blocks[i];
                var x0 = parseInt(t.attr('x'));
                var y0 = parseInt(t.attr('y'));
                var xx = parseInt(t.attr('x')) + parseInt(t.attr('width'));
                var yy = parseInt(t.attr('y')) + parseInt(t.attr('height'));
                if (p.x >= x0 && p.x <= xx && p.y >= y0 && p.y <= yy){
                  selector.offset = {x: x0+10, y: y0+10};
                  selector.pointer = {x: xx-10, y: yy-10};
                  // this will also update position of label_box
                  selector.refresh();
                  break;
                }
              }
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
              annotator.annotator_element.css('cursor', 'default');
              $('#input_' + annotator.input_shape).css('font-weight', '');
              annotator.input_shape = '';

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
      	entry.width = Math.max(30, entry.width);
      	entry.height = Math.max(30, entry.height);
      }
      var annotator, box_element, close_button, text_box;
      this.entries.push(entry);
      box_element = $('<div class="annotated_bounding_box"></div>');
      // box_element.appendTo(this.image_frame).css({
      if (entry.shape == "rectangle") {
        box_element.css({
          "background-color": entry.label,
          "opacity": 0.8,
          "position": "absolute",
          "top": (entry.top) + "px",
          "left": (entry.left) + "px",
          "width": entry.width + "px",
          "height": entry.height + "px",
          // "color": entry.label,
          "font-size": "small",
          "pointer-events": "auto"
        });
      } else if (entry.shape == "circle") {
          box_element.css({
          "background-color": entry.label,
          "opacity": 0.8,
          "border-radius": "50%",
          "position": "absolute",
          "top": (entry.top) + "px",
          "left": (entry.left) + "px",
          "width": entry.width + "px",
          "height": entry.height + "px",
          // "color": entry.label,
          "font-size": "small",
          "pointer-events": "auto"
        });
      } else if (entry.shape === 'triangle') {
         box_element.css({
          "background-color": "",
          "opacity": 0.8,
          "position": "absolute",
          "left": (entry.left) + 'px',
          "top": (entry.top) + "px",
          "border-left": entry.width/2 + "px solid transparent",
          "border-right": entry.width/2 + 'px solid transparent',
          "border-bottom": (entry.height) + "px solid " + entry.label,
          "width": "0px",
          "height": "0px",
          // "color": entry.label,
          "font-size": "small",
          "pointer-events": "auto"
        });
      } else {
        alert("known shape");
      }
      box_element.hover((function(e) {
        if (!annotator.input_shape) {
          $(this).css("cursor", "move");
        }
      }), (function(e) {
        $(this).css("cursor", "default");
      }));

      box_element.mousedown(function (e) {
        if (!annotator.input_shape && annotator.status !== "hold" && !annotator.hit_menuitem) {
          annotator.hit_menuitem = true;
          var clicked_box = $(this);
          var index = clicked_box.prevAll(".annotated_bounding_box").length;
          clicked_box.detach();
          entry = annotator.entries.splice(index, 1)[0];
          annotator.selector.start_with_existing(entry, false, true, e.pageX, e.pageY);
          annotator.input_shape = entry.shape;
          annotator.status = 'hold';
        }
      });

      // this.image_frame.prepend(box_element);
      box_element.appendTo(this.image_frame);
      var button_left = entry.width - 7;
      if (this.input_shape == 'triangle') {
        button_left = entry.width * 0.5 - 7;
      }
      close_button = $('<div class="fa fa-times-circle"></div>').appendTo(box_element).css({
        "position": "absolute",
        "top": "-10px",
        "left": button_left + "px",
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

      if (this.input_shape !== 'triangle') {
        button_left = 7;
      }

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
      //   console.log("mouse hover in");
      // }), (function(e) {
      //   console.log("mouse hover out");
      // }));

      [close_button].forEach(function (t) {
        t.hover((function (e) {
          t.fadeTo(1, 1);
        }), (function (e) {
          t.fadeTo(1, 0.06);
        }));
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
      [close_button].forEach(function (t) { t.fadeTo(800,0.06); });
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
