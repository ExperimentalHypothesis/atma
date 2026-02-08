const audio = document.getElementById("player");
const audioSource = document.getElementById("audio-source");
const listen_now_txt = document.getElementById("bt-txt");
const listen_now_icon = document.getElementById("bt-icon");

let currentChannel = 1; // Track current channel
const STREAM_BASE_URL = "https://atma.fm";
let eventSource = null; // SSE connection

// Initialize SSE connection for real-time updates
function connectSSE(channelNum) {
  // Close existing connection if any
  if (eventSource) {
    eventSource.close();
  }

  // Connect to SSE endpoint
  eventSource = new EventSource(`/api/events/channel${channelNum}`);

  eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'nowplaying') {
      const text = `${data.artist} - ${data.album}`.toLowerCase();
      document.getElementById("now-playing").textContent = text;
    }
  };

  eventSource.onerror = function(error) {
    console.error('SSE connection error:', error);
    // Will automatically reconnect
  };
}

// Connect on page load
connectSSE(currentChannel);

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

  // Reconnect SSE to new channel
  connectSSE(channelNum);
}

// Download playlist for current channel
function downloadPlaylist() {
  window.location.href = `/channel${currentChannel}.pls`;
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

// Clean up SSE connection when page unloads
window.addEventListener('beforeunload', function() {
  if (eventSource) {
    eventSource.close();
  }
});
