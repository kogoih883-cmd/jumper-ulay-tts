import asyncio
import io
import os
from flask import Flask, render_template, request, send_file
import edge_tts

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.get_json() or {}
    text = data.get('text', '')
    voice = data.get('voice', 'my-MM-NilarNeural')
    rate = data.get('rate', '+0%')

    if not text:
        return {"error": "Text is required"}, 400

    async def generate_audio():
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes

    try:
        audio_data = asyncio.run(generate_audio())
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name="jumper-u-lay-tts.mp3"
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
