# Real-Time Detection System

This project is a real-time detection system that uses various computer vision models to detect faces, hands, face mesh landmarks, and objects (like cell phones and people) in video frames received from a WebSocket connection. The detections are logged with timestamps and sent back to the frontend in real-time.

## Features

- Face Detection using MediaPipe
- Hand Detection using MediaPipe
- Face Mesh Detection using MediaPipe
- Object Detection (e.g., cell phones, people) using YOLOv5

## Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/Sharath-kumar04/Proctoring-AI-BE.git
   ```

2. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

### Running the Project

1. Start the FastAPI server:

   ```sh
   uvicorn main:app --host localhost --port 8080 --reload
   ```

2. The server will be running at `http://localhost:8080`.

### WebSocket Endpoint

- The WebSocket endpoint is available at `/ws`.
- The server receives video frames from the frontend, processes them using different detection functions, and sends back the detection logs.

## How It Works

1. **WebSocket Connection**:
   - The frontend establishes a WebSocket connection with the server at the `/ws` endpoint.
   - The server accepts the connection and enters a loop to continuously receive video frames.

2. **Frame Processing**:
   - Each received frame is decoded from bytes to an image format using OpenCV.
   - The frame is then passed to various detection functions (`detect_face`, `detect_hands`, `detect_face_mesh`, `detect_yolo`).

3. **Detection Functions**:
   - Each detection function processes the frame and logs any detected events with the current system timestamp.
   - For example, `detect_face` logs face detections, `detect_hands` logs hand detections, and so on.

4. **Sending Logs**:
   - The collected logs from all detection functions are sent back to the frontend in real-time via the WebSocket connection.
   - The logs are formatted as JSON and include the timestamp and event details.

## Project Structure

.```
├── detection
│   ├── face_detection.py
│   ├── face_mesh_detection.py
│   ├── hand_detection.py
│   ├── yolo_detection.py
│   └── __init__.py
├── main.py
├── requirements.txt
└── README.md
```

- `detection/face_detection.py`: Face detection using MediaPipe.
- `detection/face_mesh_detection.py`: Face mesh detection using MediaPipe.
- `detection/hand_detection.py`: Hand detection using MediaPipe.
- `detection/yolo_detection.py`: Object detection using YOLOv5.
- `main.py`: FastAPI server with WebSocket endpoint.
- `requirements.txt`: List of required Python packages.
- `README.md`: Project documentation.

## Notes

- The project is designed to use the GPU if available, otherwise it will fall back to using the CPU.
- Ensure that your system has the necessary drivers and libraries installed for GPU support if you intend to use the GPU.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
