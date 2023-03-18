
const globalState = {
  latestLatitude: null,
  latestLongitude: null,
  audioBlob: null
};

async function saveAudio(saveBtn) {
  try {
    if (globalState.audioBlob === null) {
      throw new Error('No audio data to save');
    }

    const datetime = new Date().toISOString().replace(/[-:.]/g, '');
    const fileName = `Recording_${datetime}.webm`;
    const jsonFileName = `Recording_${datetime}.json`;

    const fileHandle = await window.showSaveFilePicker({
      suggestedName: fileName,
      types: [
        {
          description: 'Audio files',
          accept: {
            'audio/*': ['.webm'],
          },
        },
      ],
    });

    const writableStream = await fileHandle.createWritable();
    const arrayBuffer = await globalState.audioBlob.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    await writableStream.write({ type: 'write', data: uint8Array });
    await writableStream.close();

    // Save the JSON file only if coordinates are available
    if (globalState.latestLatitude !== null && globalState.latestLongitude !== null) {
      const jsonFileHandle = await window.showSaveFilePicker({
        suggestedName: jsonFileName,
        types: [
          {
            description: 'JSON files',
            accept: {
              'application/json': ['.json'],
            },
          },
        ],
      });

      const jsonWritableStream = await jsonFileHandle.createWritable();
      const coordinates = {
        latitude: globalState.latestLatitude,
        longitude: globalState.latestLongitude,
      };
      const jsonUint8Array = new Uint8Array(new TextEncoder().encode(JSON.stringify(coordinates)));
      await jsonWritableStream.write({ type: 'write', data: jsonUint8Array });
      await jsonWritableStream.close();
    }
  } catch (err) {
      console.error('Error saving audio and JSON:', err);
    } finally {
      saveBtn.remove();
    }
}



function startTracking() {
  const gpsStatus = document.getElementById('gpsStatus');

  return navigator.geolocation.watchPosition(
    position => {
      globalState.latestLatitude = position.coords.latitude;
      globalState.latestLongitude = position.coords.longitude;
      gpsStatus.textContent = 'GPS fix acquired';
    },
    error => {
      if (error.code === error.TIMEOUT) {
        gpsStatus.textContent = 'Waiting for GPS fix...';
      } else {
        console.error('Error:', error);
        gpsStatus.textContent = `GPS error: ${error.message}`;
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    }
  );
}

function getCoords() {
  // Do something with globalState.latestLatitude and globalState.latestLongitude
  console.log('Function Latitude:', globalState.latestLatitude);
  console.log('Function Longitude:', globalState.latestLongitude);
}


document.addEventListener('DOMContentLoaded', () => {

  console.log("version 0.23")

  const recordBtn = document.getElementById('recordBtn');
  const saveBtn = document.createElement('button');
  const recordStatus = document.getElementById('recordStatus');

  const gpsButton = document.getElementById('gpsButton');
  const gpsStatus = document.getElementById('gpsStatus');

  let watchID;
  let isTracking = false;

  recordBtn.addEventListener('click', async () => {
      try {
        recordStatus.textContent = 'recording on';
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];
    
        mediaRecorder.addEventListener('dataavailable', (event) => {
          audioChunks.push(event.data);
        });
    
        mediaRecorder.start();
    
        setTimeout(() => {
          mediaRecorder.stop();
        }, 5000);
    
        mediaRecorder.addEventListener('stop', async () => {
          recordStatus.textContent = '-';
          globalState.audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    
          saveBtn.textContent = 'Save';
          recordBtn.after(saveBtn);
          saveBtn.addEventListener('click', () => saveAudio(saveBtn), { once: true });
        });
      } catch (err) {
        console.error('Error recording audio:', err);
      }
    });
        

  gpsButton.addEventListener('click', () => {
      if (!isTracking) {
          if ('geolocation' in navigator) {
              watchID = startTracking();
              gpsButton.textContent = 'Stop GPS';
              gpsStatus.textContent = 'GPS on';
              isTracking = true;
          } else {
              alert('Geolocation is not supported by your browser.');
          }
      } else {
          navigator.geolocation.clearWatch(watchID);
          gpsButton.textContent = 'Start GPS';
          gpsStatus.textContent = 'GPS off';
          isTracking = false;
      }
  });
});