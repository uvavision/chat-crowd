// The ConversationPanel module is designed to handle
// all display and behaviors of the conversation column of the app.
/* eslint no-unused-vars: "off" */
/* global Api: true, Common: true*/

var ConversationPanel = (function() {
  var settings = {
    selectors: {
      chatBox: '#scrollingChat',
      fromUser: '.from-user',
      fromAgent: '.from-agent',
      latest: '.latest'
    },
    authorTypes: {
      user: 'user',
      agent: 'agent'
    }
  };

  // Publicly accessible methods defined
  return {
    init: init,
    inputKeyDown: inputKeyDown
  };

  // Initialize the module
  function init() {
    chatUpdateSetup();
    setupInputBox();
  }
  // Set up callbacks on payload setters in Api module
  // This causes the displayMessage function to be called when messages are sent / received
  function chatUpdateSetup() {
    var currentRequestPayloadSetter = Api.setRequestPayload;
    Api.setRequestPayload = function(newPayloadStr) {
      currentRequestPayloadSetter.call(Api, newPayloadStr);
      displayMessage(JSON.parse(newPayloadStr), settings.authorTypes.user);
    };

    var currentResponsePayloadSetter = Api.setResponsePayload;
    Api.setResponsePayload = function(newPayloadStr) {
      currentResponsePayloadSetter.call(Api, newPayloadStr);
      displayMessage(JSON.parse(newPayloadStr), settings.authorTypes.agent);
    };
  }

// Set up the input box to underline text as it is typed
  // This is done by creating a hidden dummy version of the input box that
  // is used to determine what the width of the input text should be.
  // This value is then used to set the new width of the visible input box.
  function setupInputBox() {
    var input = document.getElementById('textInput');
    var dummy = document.getElementById('textInputDummy');
    var minFontSize = 14;
    var maxFontSize = 16;
    var minPadding = 4;
    var maxPadding = 6;

    // If no dummy input box exists, create one
    if (dummy === null) {
      var dummyJson = {
        'tagName': 'div',
        'attributes': [{
          'name': 'id',
          'value': 'textInputDummy'
        }]
      };

      dummy = Common.buildDomElement(dummyJson);
      document.body.appendChild(dummy);
    }

    function adjustInput() {
      if (input.value === '') {
        // If the input box is empty, remove the underline
        input.classList.remove('underline');
        input.setAttribute('style', 'width:' + '100%');
        input.style.width = '100%';
      } else {
        // otherwise, adjust the dummy text to match, and then set the width of
        // the visible input box to match it (thus extending the underline)
        input.classList.add('underline');
        var txtNode = document.createTextNode(input.value);
        ['font-size', 'font-style', 'font-weight', 'font-family', 'line-height',
          'text-transform', 'letter-spacing'].forEach(function(index) {
            dummy.style[index] = window.getComputedStyle(input, null).getPropertyValue(index);
          });
        dummy.textContent = txtNode.textContent;

        var padding = 0;
        var htmlElem = document.getElementsByTagName('html')[0];
        var currentFontSize = parseInt(window.getComputedStyle(htmlElem, null).getPropertyValue('font-size'), 10);
        if (currentFontSize) {
          padding = Math.floor((currentFontSize - minFontSize) / (maxFontSize - minFontSize)
            * (maxPadding - minPadding) + minPadding);
        } else {
          padding = maxPadding;
        }

        // var widthValue = ( dummy.offsetWidth + padding) + 'px';
        // input.setAttribute('style', 'width:' + widthValue);
        // input.style.width = widthValue;
      }
    }

    // Any time the input changes, or the window resizes, adjust the size of the input box
    input.addEventListener('input', adjustInput);
    window.addEventListener('resize', adjustInput);

    // Trigger the input event once to set up the input box and dummy element
    Common.fireEvent(input, 'input');
  }

  // Display a user or Watson message that has just been sent/received
  function displayMessage(newPayload, typeValue) {
    var isUser = isUserMessage(typeValue);
    var textExists = (newPayload.userMsg) || (newPayload.systemMsg);
    if (isUser !== null && textExists) {
      // Create new message DOM element
      var messageDivs = buildMessageDomElements(newPayload, isUser);
      var chatBoxElement = document.querySelector(settings.selectors.chatBox);
      var previousLatest = chatBoxElement.querySelectorAll((isUser
              ? settings.selectors.fromUser : settings.selectors.fromAgent)
              + settings.selectors.latest);
      // Previous "latest" message is no longer the most recent
      if (previousLatest) {
        Common.listForEach(previousLatest, function(element) {
          element.classList.remove('latest');
        });
      }

      messageDivs.forEach(function(currentDiv) {
        chatBoxElement.appendChild(currentDiv);
        // Class to start fade in animation
        currentDiv.classList.add('load');
      });
      // Move chat to the most recent messages when new messages are added
      scrollToChatBottom();
    }
  }

  // Checks if the given typeValue matches with the user "name", the Watson "name", or neither
  // Returns true if user, false if Watson, and null if neither
  // Used to keep track of whether a message was from the user or Watson
  function isUserMessage(typeValue) {
    if (typeValue === settings.authorTypes.user) {
      return true;
    } else if (typeValue === settings.authorTypes.agent) {
      return false;
    }
    return null;
  }


  // Constructs new DOM element from a message payload
  function buildMessageDomElements(newPayload, isUser) {
    var textArray = isUser ? newPayload.userMsg : newPayload.systemMsg;
    if (Object.prototype.toString.call( textArray ) !== '[object Array]') {
      textArray = [textArray];
    }
    var messageArray = [];

    textArray.forEach(function(currentText) {

      if (currentText) {
        html = $.parseHTML(currentText);
        var msg_data = html[0].lastChild.data;
        if (msg_data.startsWith('#CANVAS-')) {
          canvas_data = JSON.parse(msg_data.slice('#CANVAS-'.length));
          var canvas = document.createElement('canvas');
          var scale = 0.5;
          var textInput = document.getElementById("textInput");
          if (textInput.getAttribute("mode") === '2Dshape') {
            var canvas_width = 500;
          } else {
            var canvas_width = 600;
          }
          var canvas_height = 500;
          canvas.setAttribute("width", (canvas_width * scale).toString());
          canvas.setAttribute("height", (canvas_height * scale).toString());
          canvas.setAttribute("style", "border:3px solid #d3d3d3;");
          var ctx = canvas.getContext("2d");
          ctx.lineWidth = 4;
          ctx.setLineDash([5, 3]);
          ctx.strokeStyle = "gray";
          ctx.strokeRect(0, 0, canvas.width, canvas.height);
          ctx.setLineDash([]);
          var textInput = document.getElementById("textInput");
          if (textInput.getAttribute("mode") === '2Dshape') {
              Common.drawCanvasData(ctx, canvas_data, scale);
          } else {
              Common.drawCanvasDataCOCO(ctx, canvas_data, scale);
          }

          leafNodes = [
            {
              'tagName': 'p',
              'text': html[0].firstChild.outerHTML
            },
            {
              'tagName': 'img',
              'attributes': [{'name': 'src', 'value': canvas.toDataURL("image/png")},
                {'name': 'data', 'value': JSON.stringify(canvas_data)},
                {'name': 'height', 'value': canvas_height*scale},
                {'name': 'width', 'value': canvas_width*scale}
              ]
            }
          ];
        } else if (msg_data.startsWith('HIDDEN#CANVAS-')) {
          leafNodes = [
            {
              'tagName': 'p',
              'text': html[0].firstChild.outerHTML + "<i class=\"material-icons\" style=\"font-size:24px\">image</i>"
            }]
        } else {
          var leafNodes = [{
            // <p>{messageText}</p>
            'tagName': 'p',
            'text': currentText.replace(/\n/g, "<br>")
          }];
        }
        var messageJson = {
          // <div class='segments'>
          'tagName': 'div',
          'classNames': ['segments'],
          'children': [{
            // <div class='from-user/from-watson latest'>
            'tagName': 'div',
            'classNames': [(isUser ? 'from-user' : 'from-agent'), 'latest', ((messageArray.length === 0) ? 'top' : 'sub')],
            'children': [{
              // <div class='message-inner'>
              'tagName': 'div',
              'classNames': ['message-inner'],
              'children': leafNodes
            }]
          }]
        };
        messageArray.push(Common.buildDomElement(messageJson));
      }
    });
    return messageArray;
  }

  // Scroll to the bottom of the chat window (to the most recent messages)
  // Note: this method will bring the most recent user message into view,
  //   even if the most recent message is from Watson.
  //   This is done so that the "context" of the conversation is maintained in the view,
  //   even if the Watson message is long.
  function scrollToChatBottom() {
    var scrollingChat = document.querySelector('#scrollingChat');

    // Scroll to the latest message sent by the user
    var scrollElAgent = scrollingChat.querySelector(settings.selectors.fromAgent
            + settings.selectors.latest);
    //var scrollElUser = scrollingChat.querySelector(settings.selectors.fromUser
            //+ settings.selectors.latest);
    //scrollingChat.scrollTop = Math.max(scrollElUser.offsetTop, scrollElAgent.offsetTop);
    scrollingChat.scrollTop = 100000;
  }

  // Handles the submission of input
  function inputKeyDown(event, inputBox) {
    // Submit on enter key, dis-allowing blank messages
    if (event.keyCode === 13 && inputBox.value) {
      // Send the user message
      Api.sendRequest(inputBox.value, dialogId);

      // Clear input box for further messages
      inputBox.value = '';
      Common.fireEvent(inputBox, 'input');
    }
  }

}());
