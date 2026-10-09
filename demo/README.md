# RoadGuard AI

AI-powered pothole detection and road-condition intelligence.

## MVP pipeline
Input image/video -> OpenCV -> YOLO -> visual risk -> incident database -> dashboard -> GenAI summary/query.

## Setup
1. Create a virtual environment.
2. Install requirements.
3. Put an image in `demo/input/` or use your own path.
4. Train a pothole YOLO model and place the resulting `best.pt` at `models/pothole_best.pt`.
5. Run the detection scripts.
6. Start the API and Streamlit dashboard.

See `docs/BUILD_GUIDE.md` for the chronological build instructions.
