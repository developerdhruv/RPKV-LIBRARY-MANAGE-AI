from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import easyocr
import io
from PIL import Image as PILImage

app = FastAPI()

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

class NameResponse(BaseModel):
    name: str

@app.get("/", response_class=HTMLResponse)
async def get_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Capture ID Card</title>
        <script>
        async function startCamera() {
            const video = document.getElementById('video');
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();
        }

        async function captureImage() {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            const video = document.getElementById('video');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('file', blob, 'capture.jpg');
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                document.getElementById('result').innerText = 'Extracted Name: ' + result.name;
            });
        }
        </script>
    </head>
    <body onload="startCamera()">
        <h1>Capture ID Card</h1>
        <video id="video" width="640" height="480" autoplay></video>
        <button onclick="captureImage()">Capture</button>
        <div id="result"></div>
    </body>
    </html>
    """

@app.post("/upload", response_model=NameResponse)
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = PILImage.open(io.BytesIO(contents))

    # Use EasyOCR to extract text
    results = reader.readtext(contents)
    if results:
        # Assuming the name is in the last result
        name = results[-8][1]  # Adjust this based on your OCR output
    else:
        name = "Name not found"
    
    return {"name": name}
