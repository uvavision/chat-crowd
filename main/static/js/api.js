// The Api module is designed to handle all interactions with the server

var Api = (function() {
  var requestPayload;
  var responsePayload;
  // var messageEndpoint = '/dialog-client/api/message';
  var messageEndpoint = 'localhost:7004/mts/message';

  // Publicly accessible methods defined
  return {
    sendRequest: sendRequest,

    // The request/response getters/setters are defined here to prevent internal methods
    // from calling the methods without any of the callbacks that are added elsewhere.
    getRequestPayload: function() {
      return requestPayload;
    },
    setRequestPayload: function(newPayloadStr) {
      requestPayload = JSON.parse(newPayloadStr);
    },
    getResponsePayload: function() {
      return responsePayload;
    },
    setResponsePayload: function(newPayloadStr) {
      responsePayload = JSON.parse(newPayloadStr);
    }
  };

  // Send a message request to the server
  function sendRequest(text, role, mode) {
    // handle empty messages
    if(!text) {
      return;
    }

    // Build request payload
    var payload = {};
    payload.dialogId = role
    // if(dialogId) {
    //   payload.dialogId = dialogId
    // }

    if (payload.dialogId == 'agent') {
      payload.systemMsg = text
      Api.setResponsePayload(JSON.stringify(payload));
      // dialogId = role;
    } else {
      payload.userMsg = text
    }


    // Built http request
    if(mode == "bot") {
      // var http = new XMLHttpRequest();
      // http.open('POST', messageEndpoint, true);
      // http.setRequestHeader('Content-type', 'application/json');
      // http.onreadystatechange = function() {
      //   if (http.readyState === 4 && http.status === 200 && http.responseText) {
      //     Api.setResponsePayload(http.responseText);
      //     var jsonObj = JSON.parse(http.responseText)
      //     dialogId = jsonObj.dialogId;
      //   }
      // };
    }


    var params = JSON.stringify(payload);
    // Stored in variable (publicly visible through Api.getRequestPayload)
    // to be used throughout the application
    if (Object.getOwnPropertyNames(payload).length !== 0) {
      Api.setRequestPayload(params);
    }

    // Send request
    http.send(params);
  }
}());
