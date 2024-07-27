'use strict';

// Put variables in global scope to make them available to the browser console.
const video = window.video = document.getElementById('webcam_canvas');
const canvas = window.canvas = document.getElementById('buffer_canvas');
const out_canvas = window.out_canvas = document.getElementById('out_canvas');

const t_info = document.getElementById('time_info');

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
    width: { ideal: 99999 },
    height: { ideal: 99999 }
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
  document.getElementById("id_input").addEventListener("change", (event) => {
    refreshID();
  });
  
  document.getElementById("show_all_outlines").addEventListener("change", (event) => {
    if(document.getElementById("show_all_outlines").checked)
    {
        global_show_all_marker_outlines = 1;
    }else {
        global_show_all_marker_outlines = 0;
    }
  });
  
  document.getElementById("show_all_ids").addEventListener("change", (event) => {
    if(document.getElementById("show_all_ids").checked)
    {
        global_show_all_marker_ids = 1;
    }else {
        global_show_all_marker_ids = 0;
    }
  });
}