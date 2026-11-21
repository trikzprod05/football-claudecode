FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask requests yt-dlp numpy faster-whisper deep-translator edge-tts opencv-python-headless
COPY . .
RUN python3 -c "import flask; print(flask.__version__)"
CMD ["python3","app.py"]