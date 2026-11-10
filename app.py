from flask import Flask, request, send_file, render_template_string
import subprocess
import os
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebOlvasó - Multilingual Piper TTS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: #1e1e1e; padding: 25px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 650px; border: 1px solid #333; }
        h2 { color: #4caf50; text-align: center; margin-bottom: 20px; }
        label { font-weight: bold; color: #bbb; display: block; margin-bottom: 8px; }
        textarea { width: 100%; height: 180px; padding: 12px; border: 1px solid #444; background-color: #2a2a2a; color: #fff; border-radius: 6px; font-size: 15px; resize: vertical; box-sizing: border-box; }
        textarea:focus { outline: none; border-color: #4caf50; }
        .settings { display: flex; gap: 20px; margin: 15px 0; align-items: center; flex-wrap: wrap; }
        .setting-group { flex: 1; min-width: 200px; }
        select, input[type="range"] { width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #444; background: #2a2a2a; color: #fff; font-size: 14px; }
        .buttons { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
        button { padding: 10px 18px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 14px; color: white; transition: opacity 0.2s; }
        button:hover { opacity: 0.9; }
        .btn-play { background-color: #2e7d32; }
        .btn-stop { background-color: #c62828; }
        .btn-save { background-color: #1565c0; }
        .btn-clear { background-color: #d32f2f; width: 40px; padding: 10px 0; }
        audio { width: 100%; margin-top: 20px; display: none; }
        .status { text-align: center; margin-top: 15px; font-size: 14px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <h2>WebOlvasó v2.0 (Multilingual)</h2>
        <label for="text">Szöveg felolvasó és MP3 készítő:</label>
        <textarea id="text" placeholder="Írd ide a felolvasandó szöveget (magyar, angol vagy német)..."></textarea>

        <div class="settings">
            <div class="setting-group">
                <label for="voice">Hang és Nyelv:</label>
                <select id="voice">
                    <optgroup label="Magyar (hu_HU)">
                        <option value="hu_HU-anna-medium.onnx">Anna (Női)</option>
                        <option value="hu_HU-imre-medium.onnx">Imre (Férfi)</option>
                        <option value="hu_HU-berta-medium.onnx">Berta (Női)</option>
                    </optgroup>
                    <optgroup label="Angol (en_US)">
                        <option value="en_US-ryan-medium.onnx">Ryan (Angol)</option>
                    </optgroup>
                    <optgroup label="Német (de_DE)">
                        <option value="de_DE-thorsten-medium.onnx">Thorsten (Német)</option>
                    </optgroup>
                </select>
            </div>
            <div class="setting-group">
                <label for="speed">Sebesség (<span id="speedVal">0.65</span>x):</label>
                <input type="range" id="speed" min="0.5" max="1.5" step="0.05" value="0.65" oninput="document.getElementById('speedVal').innerText = this.value">
            </div>
        </div>

        <div class="buttons">
            <button class="btn-play" onclick="playAudio()">▶ LEJÁTSZÁS</button>
            <button class="btn-stop" onclick="stopAudio()">⏹ STOP</button>
            <button class="btn-save" onclick="saveMP3()">💾 CREATE MP3</button>
            <button class="btn-clear" onclick="clearText()" title="Törlés">❌</button>
        </div>

        <div class="status" id="status">Kész</div>
        <audio id="audioPlayer" controls></audio>
    </div>

    <script>
        const audioPlayer = document.getElementById('audioPlayer');
        const statusDiv = document.getElementById('status');

        async function playAudio() {
            const text = document.getElementById('text').value.trim();
            if (!text) { alert('Nincs szöveg!'); return; }

            statusDiv.innerText = 'Hang generálása...';
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    voice: document.getElementById('voice').value,
                    speed: document.getElementById('speed').value
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                audioPlayer.src = URL.createObjectURL(blob);
                audioPlayer.style.display = 'block';
                audioPlayer.play();
                statusDiv.innerText = 'Lejátszás folyamatban...';
            } else {
                statusDiv.innerText = 'Hiba történt a generálás során.';
            }
        }

        function stopAudio() {
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            audioPlayer.style.display = 'none';
            statusDiv.innerText = 'Leállítva';
        }

        function clearText() {
            stopAudio();
            document.getElementById('text').value = '';
        }

        async function saveMP3() {
            const text = document.getElementById('text').value.trim();
            if (!text) { alert('Nincs szöveg!'); return; }

            statusDiv.innerText = 'MP3 fájl készítése...';
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    voice: document.getElementById('voice').value,
                    speed: document.getElementById('speed').value
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'webolvaso_hang.mp3';
                document.body.appendChild(a);
                a.click();
                a.remove();
                statusDiv.innerText = 'MP3 sikeresen letöltve!';
            } else {
                statusDiv.innerText = 'Hiba az MP3 letöltésekor.';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get("text", "")
    voice = data.get("voice", "hu_HU-anna-medium.onnx")
    speed = data.get("speed", "0.65")

    model_path = os.path.join("piper", "models", voice)
    piper_cmd = ["./piper/piper", "--model", model_path, "--length_scale", str(speed), "--output_raw"]
    ffmpeg_cmd = ["ffmpeg", "-f", "s16le", "-ar", "22050", "-ac", "1", "-i", "-", "-f", "mp3", "-"]

    try:
        p1 = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(ffmpeg_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        p1.stdin.write(text.encode('utf-8'))
        p1.stdin.close()
        
        mp3_bytes = p2.stdout.read()
        return send_file(io.BytesIO(mp3_bytes), mimetype="audio/mp3")
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print("A Multilingual WebOlvasó elindult!")
    print("Megnyitás böngészőben: http://127.0.0.1:5000")
    port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
