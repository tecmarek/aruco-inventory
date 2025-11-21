'use strict';

// Put variables in global scope to make them available to the browser console.
const video = window.video = document.getElementById('webcam_canvas');
const canvas = window.canvas = document.getElementById('buffer_canvas');
const out_canvas = window.out_canvas = document.getElementById('out_canvas');

//const t_info = document.getElementById('time_info');

canvas.width = 480;
canvas.height = 360;

out_canvas.width = 480;
out_canvas.height = 360;


var global_marker_id = 0;
var global_show_all_marker_outlines = 1;
var global_show_all_marker_ids = 0;


// request video according to camera parameters
const constraints = {
  audio: false,
  video: true,
  video: {
    facingMode: 'environment',
    width: { ideal: 1600 },
    height: { ideal: 720 }
    }
};

function handleSuccess(stream) {
  window.stream = stream; // make stream available to browser console
  video.srcObject = stream;
}

function handleError(error) {
  console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
}

navigator.mediaDevices.getUserMedia(constraints).then(handleSuccess).catch(handleError);

function refreshID()
{
    global_marker_id = document.getElementById("id_input").value;
    document.getElementById("current_id").innerHTML = "Searching ID - " + global_marker_id;
}

function init_event_listener()
{
  const inputField = document.getElementById("id_input");
  if (inputField) {
    inputField.addEventListener("keydown", (event) => {
      if (event.key === 'Enter') {
        // Prevent the default browser action (like submitting a form)
        event.preventDefault();
        // This is the action that tells the mobile OS to hide the keyboard
        inputField.blur(); 
        console.log("Enter pressed. Keyboard closed.");
      }
    });

    inputField.addEventListener("change", (event) => {
      refreshID();
    });
  }
  
  const outlineButton = document.getElementById("btn-show-outlines"); 
  if (outlineButton) {
    outlineButton.addEventListener("click", () => {
        
        outlineButton.classList.toggle('active'); 

        if (outlineButton.classList.contains('active')) {
            global_show_all_marker_outlines = 1;
            console.log("Marker Outlines ON");
        } else {
            global_show_all_marker_outlines = 0;
            console.log("Marker Outlines OFF");
        }
    });
  }
  
  const idsButton = document.getElementById("btn-show-ids");
  if (idsButton) {
    idsButton.addEventListener("click", () => {
        idsButton.classList.toggle('active');

        if (idsButton.classList.contains('active')) {
            global_show_all_marker_ids = 1;
            console.log("Marker IDs ON");
        } else {
            global_show_all_marker_ids = 0;
            console.log("Marker IDs OFF");
        }
    });
  }
}