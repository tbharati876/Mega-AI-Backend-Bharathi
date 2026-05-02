import base64, io, numpy as np
from PIL import Image, ImageDraw
import face_recognition
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import uvicorn

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

def detect_face(image_array):
    faces = face_recognition.face_locations(image_array)
    if not faces:
        return None
    top, right, bottom, left = faces[0]
    return {"x": left, "y": top, "w": right-left, "h": bottom-top}

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

app = FastAPI()
latest_frame = None

HTML_PAGE = """<html><body><h2>Face Detection Running</h2></body></html>"""

@app.get("/")
def home():
    return HTMLResponse(HTML_PAGE)

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

@app.get("/video")
def get_video():
    return {"frame": latest_frame}

@app.get("/roi")
def get_roi():
    db = SessionLocal()
    data = db.query(ROI).all()
    db.close()
    return [{"x": r.x, "y": r.y, "w": r.w, "h": r.h} for r in data]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
