import * as Comlink from "https://unpkg.com/comlink/dist/esm/comlink.mjs";

var detections=[];
var last_image = null;

window.onload = (event) => {
  //Inits from main.js
  init_event_listener();
  refreshID();

  init();
}

async function init() {
  // WebWorkers use `postMessage` and therefore work with Comlink.
  const Apriltag = Comlink.wrap(new Worker("apriltag/apriltag.js"));

  // must call this to init apriltag detector; argument is a callback for when the detector is ready
  window.apriltag = await new Apriltag(Comlink.proxy(() => {

    window.apriltag.set_return_pose(0);
    window.apriltag.set_return_solutions(0);

    // start processing frames
    window.requestAnimationFrame(process_frame);
  }));
}

async function process_frame() {

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  out_canvas.width = video.videoWidth;
  out_canvas.height = video.videoHeight;


  let ctx = canvas.getContext("2d");
  let out_ctx = out_canvas.getContext("2d");

  //let imageData;
  try {

    //Display captured image
    if(last_image != null)
    {
      out_ctx.putImageData(last_image, 0, 0);
    }

    //Buffer -> capture new image
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    last_image = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
    
  } catch (err) {
    console.log("Failed to get video frame. Video not started ?");
    console.log(err);
    setTimeout(process_frame, 500); // try again in 0.5 s
    return;
  }


  // draw detection on canvas
  //Set text options
  out_ctx.textAlign = "center";
  out_ctx.textBaseline = "middle";
  out_ctx.font = "bold 60px courier";
  out_ctx.fillStyle = "#2ecc71"; //bright green

  detections.forEach(det => {

    if(det.id == global_marker_id || global_show_all_marker_outlines)
    {
      if(det.id == global_marker_id)
      {
        //found tag
        out_ctx.strokeStyle = "#e74c3c"; //Red
      }else {
        //other tags
        out_ctx.strokeStyle = "#3498db"; //Blue
      }

      // draw tag borders
      out_ctx.beginPath();

      out_ctx.lineWidth = "12";

      out_ctx.moveTo(det.corners[0].x, det.corners[0].y);
      out_ctx.lineTo(det.corners[1].x, det.corners[1].y);
      out_ctx.lineTo(det.corners[2].x, det.corners[2].y);
      out_ctx.lineTo(det.corners[3].x, det.corners[3].y);
      out_ctx.lineTo(det.corners[0].x, det.corners[0].y);

      out_ctx.stroke();
      //out_ctx.closePath();

      //Mark corner 0
      //out_ctx.strokeStyle = "#f1c40f"; //bright orange
      //out_ctx.strokeRect(det.corners[0].x - 2, det.corners[0].y - 2, 4, 4);
    }

    if(det.id == global_marker_id || global_show_all_marker_ids)
    {
      out_ctx.fillText(det.id, det.center.x, det.center.y+5);
    }
  });

  
  
  //generate grayscale image for detector from newly captured image

  let imageDataPixels = last_image.data;
  let grayscalePixels = new Uint8Array(out_ctx.canvas.width * out_ctx.canvas.height); // this is the grayscale image we will pass to the detector

  for (var i = 0, j = 0; i < imageDataPixels.length; i += 4, j++) {
    //let grayscale = Math.round((imageDataPixels[i] + imageDataPixels[i + 1] + imageDataPixels[i + 2]) / 3);

    //Fastest method found for conversion
    let grayscale = (3*imageDataPixels[i] + 4*imageDataPixels[i + 1] + imageDataPixels[i + 2]) >>> 3;

    //let grayscale = Math.round(0.2989 * imageDataPixels[i] + 0.5870 * imageDataPixels[i + 1] + 0.1140 * imageDataPixels[i + 2]);
    grayscalePixels[j] = grayscale; // single grayscale value
    //imageDataPixels[i] = grayscale;
    //imageDataPixels[i + 1] = grayscale;
    //imageDataPixels[i + 2] = grayscale;
  }
  //ctx.putImageData(imageData, 0, 0);

  
  const startTime = new Date().getTime();

  // detect aprilTag in the grayscale image given by grayscalePixels
  detections = await apriltag.detect(grayscalePixels, out_ctx.canvas.width, out_ctx.canvas.height);

  const endTime = new Date().getTime();
  const timeTaken = endTime - startTime;
  //t_info.innerHTML = "Detection time: " + timeTaken +"ms";

  window.requestAnimationFrame(process_frame);
}