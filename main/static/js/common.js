// The Common module is designed as an auxiliary module
// to hold functions that are used in multiple other modules
/* eslint no-unused-vars: "off" */

var Common = (function() {
  // Publicly accessible methods defined
  return {
    buildDomElement: buildDomElementFromJson,
    fireEvent: fireEvent,
    listForEach: listForEach,
    drawCanvasData: drawCanvasData
  };

  // Take in JSON object and build a DOM element out of it
  // (Limited in scope, cannot necessarily create arbitrary DOM elements)
  // JSON Example:
  //  {
  //    "tagName": "div",
  //    "text": "Hello World!",
  //    "className": ["aClass", "bClass"],
  //    "attributes": [{
  //      "name": "onclick",
  //      "value": "alert("Hi there!")"
  //    }],
  //    "children: [{other similarly structured JSON objects...}, {...}]
  //  }
  function buildDomElementFromJson(domJson) {
    // Create a DOM element with the given tag name
    var element = document.createElement(domJson.tagName);

    // Fill the "content" of the element
    if (domJson.text) {
      element.innerHTML = domJson.text;
    } else if (domJson.html) {
      element.insertAdjacentHTML('beforeend', domJson.html);
    }

    // Add classes to the element
    if (domJson.classNames) {
      for (var i = 0; i < domJson.classNames.length; i++) {
        element.classList.add(domJson.classNames[i]);
      }
    }
    // Add attributes to the element
    if (domJson.attributes) {
      for (var j = 0; j < domJson.attributes.length; j++) {
        var currentAttribute = domJson.attributes[j];
        element.setAttribute(currentAttribute.name, currentAttribute.value);
      }
    }
    // Add children elements to the element
    if (domJson.children) {
      for (var k = 0; k < domJson.children.length; k++) {
        var currentChild = domJson.children[k];
        element.appendChild(buildDomElementFromJson(currentChild));
      }
    }
    return element;
  }

  // Trigger an event to fire
  function fireEvent(element, event) {
    var evt;
    if (document.createEventObject) {
      // dispatch for IE
      evt = document.createEventObject();
      return element.fireEvent('on' + event, evt);
    }
    // otherwise, dispatch for Firefox, Chrome + others
    evt = document.createEvent('HTMLEvents');
    evt.initEvent(event, true, true); // event type,bubbling,cancelable
    return !element.dispatchEvent(evt);
  }

  // A function that runs a for each loop on a List, running the callback function for each one
  function listForEach(list, callback) {
    for (var i = 0; i < list.length; i++) {
      callback.call(null, list[i]);
    }
  }

    /// expand with color, background etc.
  function drawTextBG(ctx, txt, font, x, y) {

      ctx.save();
      ctx.font = font;
      ctx.textBaseline = 'top';
      ctx.fillStyle = 'rgba(255, 165, 0, 0.5)';

      var width = ctx.measureText(txt).width;
      ctx.fillRect(x, y, width, parseInt(font, 10));

      ctx.fillStyle = '#000';
      ctx.fillText(txt, x, y);

      ctx.restore();
  }

    function drawCanvasData(ctx, canvas_data, scale) {
        ctx.strokeStyle = 'rgba(255, 0, 0, 0.2)';
        canvas_data.forEach(function (box_anno) {
            bbox = [box_anno['left'], box_anno['top'], box_anno['width'], box_anno['height']];
            ctx.rect(bbox[0] * scale, bbox[1] * scale, (bbox[2]) * scale, (bbox[3]) * scale);
            ctx.stroke();
            drawTextBG(ctx, box_anno['label'], '15px arial', bbox[0] * scale, bbox[1] * scale);
        });
    }

}());
