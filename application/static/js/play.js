const audio = document.getElementById("player");
const audioSource = document.getElementById("audio-source");
const listen_now_txt = document.getElementById("bt-txt");
const listen_now_icon = document.getElementById("bt-icon");

let currentChannel = 1; // Track current channel
const STREAM_BASE_URL = "http://173.212.246.158:7778";

function toggle_play() {
  if (audio.paused) {
    audio.play();
    listen_now_txt.innerHTML = "stop";
    listen_now_icon.className = "fas fa-volume-mute player-button-icon";
  } else {
    audio.pause();
    listen_now_txt.innerHTML = "listen";
    listen_now_icon.className = "fa fa-volume-up player-button-icon";
  }
}

// Switch between channels
function switchChannel(channelNum) {
  // Stop current playback
  audio.pause();

  // Update channel
  currentChannel = channelNum;
  audioSource.src = `${STREAM_BASE_URL}/channel${channelNum}`;
  audio.load();

  // Reset UI to stopped state
  listen_now_txt.innerHTML = "listen";
  listen_now_icon.className = "fa fa-volume-up player-button-icon";

  // Update tab styling
  document.getElementById("tab-channel1").classList.toggle("active", channelNum === 1);
  document.getElementById("tab-channel2").classList.toggle("active", channelNum === 2);

  // Update currently playing text
  document.getElementById("now-playing").textContent = "loading...";

  // Fetch current song for the new channel
  fetchNowPlaying(channelNum);
}

// Download playlist for current channel
function downloadPlaylist() {
  window.location.href = `/channel${currentChannel}.pls`;
}

// Fetch currently playing song for a channel
function fetchNowPlaying(channelNum) {
  fetch(`/api/song/channel${channelNum}`)
    .then(response => response.json())
    .then(data => {
      const text = `${data.artist} - ${data.album}`.toLowerCase();
      document.getElementById("now-playing").textContent = text;
    })
    .catch(error => {
      console.error('Error fetching now playing:', error);
      document.getElementById("now-playing").textContent = "unknown artist - unknown song";
    });
}

// Update UI if audio state changes externally (e.g., ended, error)
audio.onplaying = function () {
  listen_now_txt.innerHTML = "stop";
  listen_now_icon.className = "fas fa-volume-mute player-button-icon";
};

audio.onpause = function () {
  listen_now_txt.innerHTML = "listen";
  listen_now_icon.className = "fa fa-volume-up player-button-icon";
};

audio.onended = function () {
  listen_now_txt.innerHTML = "listen";
  listen_now_icon.className = "fa fa-volume-up player-button-icon";
};
