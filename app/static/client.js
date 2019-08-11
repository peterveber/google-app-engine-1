var el = x => document.getElementById(x);
/////////////////////////////////////////////////////////////
// Set constraints for the video stream
var constraints = { video: { facingMode: "environment" }, audio: false };
var track = null;

// Define constants
const cameraView = document.querySelector("#camera--view"),
    cameraOutput = document.querySelector("#camera--output"),
    cameraSensor = document.querySelector("#camera--sensor"),
    cameraTrigger = document.querySelector("#camera--trigger");

// Access the device camera and stream to cameraView
function cameraStart() {
    navigator.mediaDevices
        .getUserMedia(constraints)
        .then(function(stream) {
            track = stream.getTracks()[0];
            cameraView.srcObject = stream;
        })
        .catch(function(error) {
            console.error("Oops. Something is broken.", error);
        });
}

// Take a picture when cameraTrigger is tapped
cameraTrigger.onclick = function() {
    cameraSensor.width = cameraView.videoWidth;
    cameraSensor.height = cameraView.videoHeight;
    cameraSensor.getContext("2d").drawImage(cameraView, 0, 0);
    cameraOutput.src = cameraSensor.toDataURL("image/webp");
    cameraOutput.classList.add("taken");
    //el("upload-label").innerHTML = cameraSensor.toDataURL("image/webp");
    //el("file-input").files = cameraSensor.toDataURL("image/webp");
    //var image = cameraSensor.toDataURL("image/png").replace("image/png", "image/octet-stream");  // here is the most important part because if you dont replace you will get a DOM 18 exception.
    //window.location.href=image; // it will save locally
    
    var canvas = document.getElementById("camera--sensor");
    var img    = canvas.toDataURL("image/png");
    //document.write('<img src="'+img+'"/>');
    //el("file-input").files = document.write('<img src="'+img+'"/>');
    
    var canvas = document.getElementById("camera--output");
    //var context = canvas.getContext('2d');
    //el("file-input").files = file.files[0];
    //el("file-input").files = context.toDataURL();
       
    analyze();
    
    //var reader = new FileReader();
    //reader.onload = function(e) {
    //el("image-picked").src = cameraSensor.toDataURL("image/webp");
    //el("image-picked").className = "";
        

  //};
  //reader.readAsDataURL(cameraSensor.toDataURL("image/webp"));
    // track.stop();
};

function dataURItoBlob(dataURI) {
    // convert base64/URLEncoded data component to raw binary data held in a string
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    // write the bytes of the string to a typed array
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type:mimeString});
}

// Start the video stream when the window loads
window.addEventListener("load", cameraStart, false);
/////////////////////////////////////////

function analyze() {
  var canvas = document.getElementById("camera--sensor");
  var dataURL    = canvas.toDataURL("image/png");
  //var canvas = document.getElementById("camera--output");
  //var dataURL = canvas.toDataURL("image/png");
  var blob = dataURItoBlob(dataURL);
  var filex = new File([blob], "filename");
  var uploadFiles = filex;

  if (uploadFiles.size < 10) alert("Something is wrong with image!");

  el("result-label").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
  xhr.onerror = function() {alert (xhr.responseText);}
  xhr.onload = function(e) {
    if (this.readyState === 4) {
      var response = JSON.parse(e.target.responseText);
      el("result-label").innerHTML = `Result = ${response["result"]}`;
    }
    //el("analyze-button").innerHTML = "Analyze";
  };
       
  var fileData = new FormData();
  fileData.append("file", uploadFiles);
  xhr.send(fileData);
}
