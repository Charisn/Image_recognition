function startCameraVideo(videoId) {
  const videoElement = document.getElementById(videoId);

  if (!videoElement) {
    console.error(`Video element with ID '${videoId}' not found.`);
    return Promise.reject(new Error('Video element not found'));
  }

  const constraints = {
    video: { facingMode: { ideal: "environment" } },
    audio: false,
  };

  return navigator.mediaDevices.getUserMedia(constraints)
    .then((stream) => {
      videoElement.srcObject = stream;
      return videoElement.play();
    })
    .catch((err) => {
      console.error('Error accessing the camera:', err);
      throw err;
    });
}

function captureToCanvas(videoElementId, canvasElementId, quality = 1.0) {
  const video = document.getElementById(videoElementId);
  const canvas = document.getElementById(canvasElementId);
  const context = canvas.getContext('2d');

  if (!video || video.readyState !== 4) {
    console.error("Video not ready");
    return null;
  }

  // Adjust canvas size
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // Draw the current frame
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert canvas to Base64 string
  return canvas.toDataURL('image/jpeg', quality);
}
