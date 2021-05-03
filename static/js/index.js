let newestTimestamp = 0;

function setServerStatusDown(){
  $(".server_status").removeClass("server_up");
  $(".server_status").addClass("server_down");
  $(".server_status").text("Down");
}

function setServerStatusUp(){
  $(".server_status").removeClass("server_down");
  $(".server_status").addClass("server_up");
  $(".server_status").text("Running");
}

function getComments(){
  fetch(`/comments?timestamp=${encodeURIComponent(newestTimestamp)}`, {
    method: 'GET',
    credentials: 'include',
  })
  .then(function(response) {
    if(response.status < 300){
      return response.json();
    } else {
      let ok = confirm("Comment stream error. You need to refresh this page. Click OK to refresh.");
      if(ok){
        window.location = "/"
      }
      return null;
    }
  })
  .then(function(data){
    if(data != null && !data.hasOwnProperty("error")) {
      addComments(data.comments);
    }
  })
  .catch(function(err) {
    alert(err.message);
  });
}

function addComment(commentObj){
  if(commentObj["timestamp_float"] > newestTimestamp) newestTimestamp=commentObj["timestamp_float"];
  let author = commentObj["comment"]["author"];
  let message = commentObj["comment"]["message"];
  let comment = $("<div>").addClass("comment")
    .append($("<div>").addClass("smallestFont").text(author))
    .append($("<div>").addClass("smallFont").html(message))//will render comment as HTML - useful for bold font, but probably don't want to do this in a real world scenario
  $("#comments").append(comment);
  if($("#comments").children().length > 10){
    $($("#comments").children()[0]).remove();
  }
  if($("#comments").children().length > 9){
    $($("#comments").children()[0]).css('opacity', '0.4');
    $($("#comments").children()[1]).css('opacity', '0.7');
  } else if($("#comments").children().length > 8){
    $($("#comments").children()[0]).css('opacity', '0.7');
  }
}

function addComments(comments, startup){
  for(let i in comments){
    if(startup || comments[i]["comment"]["type"] != "system") addComment(comments[i]);
  }
}

async function toggleServer(isRunning){
  fetch('/toggle', {
    method: 'POST',
    credentials: 'include',
    body: JSON.stringify({"isRunning":isRunning}),
  })
  .then(response => response.json())
  .then(function(data){
    //console.log(data)
    addComment(data);
  })
  .catch(function(err) {
    alert(err.message);
  });
}

$(document).ready(function() {
  var src = $(document.body).css('background-image');
  var url = src.match(/\((.*?)\)/)[1].replace(/('|")/g,'');

  var img = new Image();
  img.onload = function() {
    $("#container").show();
  }
  img.src = url;
  if (img.complete) img.onload();
  if(app != null){
    console.log(app);
    if(app["server_status"] == false){
      $( "#server" ).prop( "checked", true );
      setServerStatusDown();
    } else {
      $( "#server" ).prop( "checked", false ); //the else condition shouldn't be necessary, but it's here in case of browser cache.
    }
    addComments(app["comments"], true);
  }
  setInterval(getComments, 5000);

  $("#server").on("change", function(e){
    if($(e.target).prop('checked')){
      setServerStatusDown();
      toggleServer(false);
    } else {
      setServerStatusUp();
      toggleServer(true);
    }
  })
})
