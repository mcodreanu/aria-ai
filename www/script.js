$(document).ready(function () {
  function triggerAssistant() {
    eel.play_assistant_sound();
    eel.all_commands()();
  }

  // Click event for the microphone button
  $("#mic-button").click(triggerAssistant);

  function docKeyUp(e) {
    if (e.key === 'a' && e.metaKey) {
      triggerAssistant();
    }
  }

  document.addEventListener('keyup', docKeyUp, false);

  function playAssistant(message) {
    if (message != "") {
      eel.all_commands(message);
      $("#chatbox").val("");
    }
  }

  $("#send-button").click(function () {
    let message = $("#chatbox").val();
    playAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    key = e.which;

    if (key == 13) {
      let message = $("#chatbox").val();
      playAssistant(message)
    }
  });

  $("#stop-button").click(function () {
    eel.stop_audio()
    document.getElementById("audio-controls").hidden = true;
  });

  $("#volumeSlider").click(function () {
    const volume = document.getElementById("volumeSlider").value / 100;
    eel.set_volume(volume);
  });
});


