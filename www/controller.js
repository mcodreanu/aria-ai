$(document).ready(function () {
  eel.expose(DisplayMessage)
  function DisplayMessage(message) {
    $(".ai-message").text(message);
  }

  eel.expose(ShowMainPage)
  function ShowMainPage() {
    $(".ai-message").text("Ask me anything!");
  }

  eel.expose(senderText)
  function senderText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-end mb-4"> <div class="width-size"> <div class="sender_message">${message}</div></div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(receiverText)
  function receiverText(message) {
    var chatBox = document.getElementById("chat-canvas-body");

    if (message.trim() != "") {
      chatBox.innerHTML += `<div class="row justify-content-start mb-4"> <div class="width-size"> <div class="receiver_message">${message}</div></div></div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(showAudioControls)
  function showAudioControls() {
    var audioControls = document.getElementById("audio-controls");
    audioControls.hidden = false;
  }

  eel.expose(hideAudioControls)
  function hideAudioControls() {
    var audioControls = document.getElementById("audio-controls");
    audioControls.hidden = true;
    audioControls.value = "50";
  }

  eel.expose(updateAudioProgress);
  function updateAudioProgress(progress, currentTime, totalTime) {
    // Update progress bar
    document.getElementById("progressBar").value = progress;

    // Update current time
    document.getElementById("currentTime").innerText = formatTime(currentTime);
    document.getElementById("totalTime").innerText = formatTime(totalTime);
  }

  // Utility function to format time in mm:ss
  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  }

  eel.expose(showImageCreated);
  function showImageCreated(path) {
    var image = document.getElementById("image-created");
    var canvas = document.getElementById("canvasOne");
    var aiAnimation = document.getElementById("ai-animation");
    canvas.hidden = true;
    aiAnimation.hidden = true;
    image.src = path;
    console.log(image.src);
    image.hidden = false;
  }
});