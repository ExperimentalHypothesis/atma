const audio = document.getElementById("player");
const listen_now_txt = document.getElementById("bt-txt")
const listen_now_icon = document.getElementById("bt-icon")

function toggle_play() {
  if (audio.paused) {
    audio.play();
    listen_now_txt.innerHTML = "stop now";
    listen_now_icon.className = "fas fa-volume-mute player-button-icon";
  } else {
    audio.pause();
    listen_now_txt.innerHTML = "listen now";
    listen_now_icon.className = "fa fa-volume-up player-button-icon";
  }
};

// Update UI if audio state changes externally (e.g., ended, error)
audio.onplaying = function () {
  listen_now_txt.innerHTML = "stop now";
  listen_now_icon.className = "fas fa-volume-mute player-button-icon";
};

audio.onpause = function () {
  listen_now_txt.innerHTML = "listen now";
  listen_now_icon.className = "fa fa-volume-up player-button-icon";
};

audio.onended = function () {
  listen_now_txt.innerHTML = "listen now";
  listen_now_icon.className = "fa fa-volume-up player-button-icon";
};
