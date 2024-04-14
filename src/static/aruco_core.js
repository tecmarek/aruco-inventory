var video, canvas, context, imageData, detector;
  
    function onLoad(){
      video = document.getElementById("video");
      canvas = document.getElementById("canvas");
      context = canvas.getContext("2d");
    
      canvas.width = parseInt(canvas.style.width);
      canvas.height = parseInt(canvas.style.height);
      
      if (navigator.mediaDevices === undefined) {
        navigator.mediaDevices = {};
      }
      
      if (navigator.mediaDevices.getUserMedia === undefined) {
        navigator.mediaDevices.getUserMedia = function(constraints) {
          var getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
          
          if (!getUserMedia) {
            return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
          }

          return new Promise(function(resolve, reject) {
            getUserMedia.call(navigator, constraints, resolve, reject);
          });
        }
      }
      
      navigator.mediaDevices
        .getUserMedia({ video: {
            facingMode: 'environment',
            width: { ideal: 99999 },
            height: { ideal: 99999 }
            }, audio: false})
        .then(function(stream) {
          if ("srcObject" in video) {
            video.srcObject = stream;
            video.play();
          } else {
            video.src = window.URL.createObjectURL(stream);
          }
        })
        .catch(function(err) {
          console.log(err.name + ": " + err.message);
        }
      );
        
      detector = new AR.Detector({
        dictionaryName: 'ARUCO'
      });

      requestAnimationFrame(animate); //was tick
    }

    const fps = 20;
    function animate() {
        tick()

        setTimeout(() => {
            requestAnimationFrame(animate);
        }, 1000 / fps);
    }
    
    function tick(){
      //requestAnimationFrame(tick);
      
      if (video.readyState === video.HAVE_ENOUGH_DATA){
        snapshot();

        var markers = detector.detect(imageData);
        drawCorners(markers, global_marker_id);
        drawId(markers, global_marker_id);
      }
    }

    function snapshot(){
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    }
          
    function drawCorners(markers, showID){
      var corners, corner, i, j;
    
      context.lineWidth = 3;

      for (i = 0; i !== markers.length; ++ i){
        corners = markers[i].corners;
        
        if(markers[i].id == showID || global_show_all_marker_outlines)
        {
            if(markers[i].id == showID)
            {
                context.strokeStyle = "#3498db";
            }else {
                context.strokeStyle = "red";
            }
            
            context.beginPath();
            
            for (j = 0; j !== corners.length; ++ j){
                corner = corners[j];
                context.moveTo(corner.x, corner.y);
                corner = corners[(j + 1) % corners.length];
                context.lineTo(corner.x, corner.y);
            }

            context.stroke();
            context.closePath();
            
            context.strokeStyle = "#f1c40f";
            context.strokeRect(corners[0].x - 2, corners[0].y - 2, 4, 4);
        }
        
      }
    }

    function drawId(markers, showID){
      var corners, corner, x_min, y_min, x_max, y_max, i, j;
      
      //context.strokeStyle = "#d35400";
      //context.lineWidth = 1;

      context.textAlign = "center";
      context.textBaseline = "middle";
      context.font = "bold 32px courier";
      context.fillStyle = "#34eb37";
      
      for (i = 0; i !== markers.length; ++ i){
        corners = markers[i].corners;
        
        x_min = Infinity;
        y_min = Infinity;
        x_max = 0;
        y_max = 0;
        
        if(markers[i].id == showID || global_show_all_marker_ids)
        {
            for (j = 0; j !== corners.length; ++ j){
                corner = corners[j];
                
                x_min = Math.min(x_min, corner.x);
                y_min = Math.min(y_min, corner.y);
      
                x_max = Math.max(x_max, corner.x);
                y_max = Math.max(y_max, corner.y);
              }
      
              x_diff = x_max-x_min;
              y_diff = y_max-y_min;
      
              context.fillText(markers[i].id, x_min + x_diff/2, y_min + y_diff/2)
        }
      }
    }

    window.onload = onLoad;