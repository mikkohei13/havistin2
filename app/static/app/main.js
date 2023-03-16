const recordBtn = document.getElementById('recordBtn');
const saveBtn = document.createElement('button');
let audioBlob;

recordBtn.addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm; codecs=pcm' });
    const audioChunks = [];

    mediaRecorder.addEventListener('dataavailable', (event) => {
      audioChunks.push(event.data);
    });

    mediaRecorder.start();

    setTimeout(() => {
      mediaRecorder.stop();
    }, 5000);

    mediaRecorder.addEventListener('stop', async () => {
      const webmBlob = new Blob(audioChunks, { type: 'audio/webm' });
      audioBlob = await convertWebmToWav(webmBlob);

      saveBtn.textContent = 'Save';
      recordBtn.after(saveBtn);
      saveBtn.addEventListener('click', saveAudio, { once: true });
    });
  } catch (err) {
    console.error('Error recording audio:', err);
  }
});

async function saveAudio() {
  try {
    const datetime = new Date().toISOString().replace(/[-:.]/g, '');
    const fileName = `Recording_${datetime}.wav`;

    const fileHandle = await window.showSaveFilePicker({
      suggestedName: fileName,
      types: [
        {
          description: 'Audio files',
          accept: {
            'audio/*': ['.wav'],
          },
        },
      ],
    });

    const writableStream = await fileHandle.createWritable();
    await writableStream.write(audioBlob);
    await writableStream.close();

    saveBtn.remove();
  } catch (err) {
    console.error('Error saving audio:', err);
  }
}

async function convertWebmToWav(webmBlob) {
  return new Promise(async (resolve) => {
    const arrayBuffer = await webmBlob.arrayBuffer();
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const numberOfChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = {
      numberOfChannels: numberOfChannels,
      sampleRate: sampleRate,
    };

    const wavData = audioBufferToWav(audioBuffer, format);
    const wavBlob = new Blob([wavData], { type: 'audio/wav' });
    resolve(wavBlob);
  });
}

function audioBufferToWav(buffer, format) {
  const data = encodeWav(buffer, format);
  return new Uint8Array(data).buffer;
}

function encodeWav(buffer, format) {
  const numberOfChannels = format.numberOfChannels;
  const sampleRate = format.sampleRate;
  const bitDepth = 16;

  const byteRate = (sampleRate * numberOfChannels * bitDepth) / 8;
  const dataSize = buffer.getChannelData(0).length * numberOfChannels * (bitDepth / 8);
  const bufferLength = 44 + dataSize;

  const dataView = new DataView(new ArrayBuffer(bufferLength));

  writeString(dataView, 0, 'RIFF');
  dataView.setUint32(4, 36 + dataSize, true);
    writeString(dataView, 8, 'WAVE');
    writeString(dataView, 12, 'fmt ');
    dataView.setUint32(16, 16, true);
    dataView.setUint16(20, 1, true);
    dataView.setUint16(22, numberOfChannels, true);
    dataView.setUint32(24, sampleRate, true);
    dataView.setUint32(28, byteRate, true);
    dataView.setUint16(32, numberOfChannels * (bitDepth / 8), true);
    dataView.setUint16(34, bitDepth, true);
    writeString(dataView, 36, 'data');
    dataView.setUint32(40, dataSize, true);

    const channelDataArrays = [];
    for (let channel = 0; channel < numberOfChannels; channel++) {
        channelDataArrays.push(new Int16Array(buffer.getChannelData(channel).map(sample => sample * 32767)));
    }

    for (let i = 0; i < channelDataArrays[0].length; i++) {
        for (let channel = 0; channel < numberOfChannels; channel++) {
        dataView.setInt16(44 + (i * numberOfChannels + channel) * 2, channelDataArrays[channel][i], true);
        }
    }

    return dataView;
    }

    function writeString(dataView, offset, string) {
    for (let i = 0; i < string.length; i++) {
        dataView.setUint8(offset + i, string.charCodeAt(i));
    }
    }
  