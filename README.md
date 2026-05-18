

# Real-Time Face Detection Video Streaming System

## Overview

This project implements a **real-time face detection video streaming system** using FastAPI and WebSockets.
It captures video from the browser, detects faces without using OpenCV, draws a bounding box (ROI), stores ROI data in a database, and streams the processed frames back to the frontend.

---

## Features

* Real-time video streaming from browser.
* WebSocket based frame transfer.
* Face detection using `face_recognition` (no OpenCV).
* ROI (Region of Interest) extraction and storage.
* Bounding box drawn using Pillow.
* Database storage (SQLite).
* REST APIs for fetching video and ROI data.
* Docker support for containerized deployment.
* Public demo via ngrok (Colab).

---

## Architecture

The system follows this pipeline:

User (Browser)
→ Frontend (HTML + JS Camera Capture)
→ WebSocket (`/ws/video`)
→ FastAPI Backend
→ Face Detection (`face_recognition`)
→ ROI Processing (Pillow)
→ Database (SQLite)
→ REST APIs (`/video`, `/roi`)

See `architecture.png` for visual diagram.

---

## API Endpoints

### 1. WebSocket

* **`/ws/video`**

  * Sends video frames from frontend
  * Returns processed frames with ROI

### 2. REST APIs

* **`/video`**

  * Returns latest processed frame

* **`/roi`**

  * Returns stored ROI data:

  ```json
  [
    {
      "x": 100,
      "y": 120,
      "w": 80,
      "h": 80,
      "timestamp": "2026-01-01 10:00:00"
    }
  ]
  ```

---

## Tech Stack

* **Backend:** FastAPI
* **Streaming:** WebSockets
* **Face Detection:** face_recognition
* **Image Processing:** Pillow
* **Database:** SQLite
* **Containerization:** Docker
* **Frontend:** HTML + JavaScript
* **Demo Hosting:** ngrok (Colab)

---

## 📁 Project Structure

```
face-detection-system/
│
├── main.py                # Docker compatible backend
├── demo_colab.ipynb       # ngrok demo version
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── architecture.png
├── test_api.py
└── README.md
```

---

## Testing

Run basic tests:

```bash
python test_api.py
```

---

## Assumptions

* Only **one face** is present in the video.
* Frames are processed at ~200ms intervals.
* SQLite is used for simplicity (can be replaced with PostgreSQL).

---

## Security Notes

* No authentication implemented (demo purpose).
* Input validation assumed from controlled frontend.
* ngrok used only for demo exposure.

---

## AI Usage Disclosure

AI tools were used for:

* Designing Docker setup
* Documentation assistance

All code was reviewed, modified, and tested manually.

---

## Notes

* **Demo version** uses ngrok for public access.
* **Docker version** is production-oriented.
* Docker execution is recommended locally.

---

## Evaluation Checklist

✔ 3 API endpoints implemented.
✔ WebSocket streaming.
✔ Face detection without OpenCV.
✔ ROI extraction and storage.
✔ Bounding box rendering.
✔ Database integration.
✔ Docker setup.
✔ Frontend included.
✔ Architecture diagram included.

---


