function copyFull() {
  //copys inner html of target div.
  //event button
  var copyBtn = $('.copy-btn');
  copyBtn.on('click', function(event) {
    // alert("full?");

    var $this = $(this);

    //find the element that has the text you want.
    var content = $this.prev('.copy-content');
    //creates new range object and sets text as boundaries.
    var range = document.createRange();
    range.selectNode(content[0]);
    window.getSelection().addRange(range);

    try {
      // Now that we've selected the text, execute the copy command
      var successful = document.execCommand('copy');
      /*var msg = successful ? 'successful' : 'unsuccessful';
      console.log('Copy email command was ' + msg);*/

      //handle success
      $(this).after('<span class="success"></span>');
      setTimeout(function() {
        $('.success').addClass('show');
        setTimeout(function() {
          $('.success').fadeOut(function() {
            $('.success').remove();
          });
        }, 1000);
      }, 0);
    } catch (err) {
      //console.log('Oops, unable to copy');
    }
    //clear out range for next event.
    window.getSelection().removeAllRanges();

  });
}

function copyPhone() {
  // same principle. Set a copyBtn, and a target element. In this case they are the same.
  var copyBtn = $('.phone');
  copyBtn.on('click', function(event) {
    var content = $(this);
    var range = document.createRange();
    // var referenceNode = document.getElementsByTagName("textarea").item(0)
    range.selectNode(content[0]);
    // range.selectNode(referenceNode);
    window.getSelection().addRange(range);

    try {
      var successful = document.execCommand('copy');
      $(this).addClass('p-success');
      setTimeout(function() {
        $('.phone').removeClass('p-success');
      }, 1000);
    } catch (err) {
      // console.log('Oops, unable to copy');
    }

    window.getSelection().removeAllRanges();

  });
}

$(function() {
  copyFull();
  copyPhone();

});
