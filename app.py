import base64, io, numpy as np
from PIL import Image, ImageDraw
import face_recognition
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import nest_asyncio, uvicorn
from pyngrok import ngrok

nest_asyncio.apply()

NGROK_AUTH_TOKEN = "PASTE_NGROK_TOKEN_HERE"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# DATABASE (SQLite)

DATABASE_URL = "sqlite:///./roi.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ROI(Base):
    __tablename__ = "roi"
    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    w = Column(Float)
    h = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)


# FACE DETECTION (NO OpenCV)

def detect_face(image_array):
    faces = face_recognition.face_locations(image_array)
    if not faces:
        return None

    top, right, bottom, left = faces[0]
    return {"x": left, "y": top, "w": right-left, "h": bottom-top}


# DRAW ROI

def draw_box(image_bytes, roi):
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)

    if roi:
        draw.rectangle(
            [(roi["x"], roi["y"]),
             (roi["x"]+roi["w"], roi["y"]+roi["h"])],
            outline="red", width=3
        )

    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

# FASTAPI APP

app = FastAPI()
latest_frame = None

# FRONTEND

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Face Detection Stream</title>
</head>
<body>
<h2>Live Camera</h2>
<video id="video" autoplay></video>

<h2>Processed Feed</h2>
<img id="output"/>

<script>
const ws = new WebSocket(window.location.origin.replace("http","ws") + "/ws/video");

navigator.mediaDevices.getUserMedia({video:true})
.then(stream => {
    const video = document.getElementById("video");
    video.srcObject = stream;

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.drawImage(video, 0, 0);

        const data = canvas.toDataURL("image/jpeg").split(",")[1];
        ws.send(data);
    }, 200);
});

ws.onmessage = (event) => {
    document.getElementById("output").src =
        "data:image/jpeg;base64," + event.data;
};
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return HTMLResponse(HTML_PAGE)

# WEBSOCKET STREAM

@app.websocket("/ws/video")
async def video_stream(ws: WebSocket):
    await ws.accept()
    global latest_frame

    while True:
        data = await ws.receive_text()
        image_bytes = base64.b64decode(data)

        image = np.array(Image.open(io.BytesIO(image_bytes)))
        roi = detect_face(image)

        if roi:
            db = SessionLocal()
            db.add(ROI(**roi))
            db.commit()
            db.close()

        processed = draw_box(image_bytes, roi)
        latest_frame = processed

        await ws.send_text(processed)

# REST APIs

@app.get("/video")
def get_video():
    return {"frame": latest_frame}

@app.get("/roi")
def get_roi():
    db = SessionLocal()
    data = db.query(ROI).all()
    db.close()

    return [
        {
            "x": r.x,
            "y": r.y,
            "w": r.w,
            "h": r.h,
            "timestamp": str(r.timestamp)
        }
        for r in data
    ]


# RUN SERVER + NGROK

public_url = ngrok.connect(8000)
print("PUBLIC URL:", public_url)


config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
server = uvicorn.Server(config)

await server.serve()
