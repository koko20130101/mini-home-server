import json
import base64
import websockets
import ssl
from io import BytesIO
from http import HTTPStatus
import urllib.request
from django.core.cache import cache

# minimax
MODULE = "speech-01-turbo"
EMOTION = "happy"

API_KEY = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJrb2tvIiwiVXNlck5hbWUiOiJrb2tvIiwiQWNjb3VudCI6IiIsIlN1YmplY3RJRCI6IjE5MTA4OTA4MzcwNjQwMzI1NDEiLCJQaG9uZSI6IjE3NzI4MTQwODQwIiwiR3JvdXBJRCI6IjE5MTA4OTA4MzcwNTU2NDM5MzMiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiIiLCJDcmVhdGVUaW1lIjoiMjAyNS0wNC0xMiAxNzo0Mjo1OSIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.PedssEhOQVd_2HKRPTJNLuEKZ3DsHDX6WAcB_P4jdAF6ytSLHLUjdYTis4bZwhzGl98nFbYtspN8_c8JRFpqn1_sICvIR3OFAXY46LZi17sMH5xeJbldjODqYSQf3CQBpqA4ywgDhtqSeYl4833yKwE4lDDddmmvQ9H3wox9NpOo3bpg19cPtqFM6QOp-iYJlCY6EPbOJsMbdOD1t9RX1B6EP1Bn5H2O5th_DmGjTrvwZj85MoSXBYv3ikl1Vl-sc7s5bLptX7lnfE8KMOznkIRJO9SrHUrloDBoU00SN_UbLa6gmBt64HCDeGSefaEs6O80jB7SYy8qchTueQv2tA'


''' ============ minimax文本转语音模型 ============ '''


async def establish_connection():
    """建立WebSocket连接"""
    url = "wss://api.minimax.chat/ws/v1/t2a_v2"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        ws = await websockets.connect(url, additional_headers=headers, ssl=ssl_context)
        connected = json.loads(await ws.recv())
        if connected.get("event") == "connected_success":
            print("连接成功")
            return ws
        return None
    except Exception as e:
        print(f"连接失败: {e}")
        return None


async def start_task(websocket):
    """发送任务开始请求"""
    start_msg = {
        "event": "task_start",
        "model": MODULE,
        "voice_setting": {
            "voice_id": "male-qn-qingse",
            "speed": 1,
            "vol": 1,
            "pitch": 0,
            "emotion": EMOTION
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    await websocket.send(json.dumps(start_msg))
    response = json.loads(await websocket.recv())
    return response.get("event") == "task_started"


async def close_connection(websocket):
    """关闭连接"""
    if websocket:
        await websocket.send(json.dumps({"event": "task_finish"}))
        await websocket.close()
        print("连接已关闭")


async def text_to_audio(text: str, chunk_callback):
    ws = await establish_connection()
    if not ws:
        return

    try:
        if not await start_task(ws):
            print("任务启动失败")
            return

        """发送继续请求并收集音频数据"""
        await ws.send(json.dumps({
            "event": "task_continue",
            "text": text
        }))
        audio_chunks = []
        hunk_counter = 0  # 分块计数器
        while True:
            response = json.loads(await ws.recv())
            if "data" in response and "audio" in response["data"]:
                audio = response["data"]["audio"]
                audio_chunks.append(audio)
                if len(audio_chunks) > 30:
                    hunk_counter += 1
                    # 每30个音频块返回一次
                    base64_audio = base64.b64encode(bytes.fromhex(
                        "".join(audio_chunks))).decode('utf-8')
                    await chunk_callback('base64', base64_audio)
                    audio_chunks = []

            if response.get("is_final"):
                if len(audio_chunks) > 0:
                    base64_audio = base64.b64encode(bytes.fromhex(
                        "".join(audio_chunks))).decode('utf-8')
                    await chunk_callback('base64', base64_audio)

                break
    finally:
        await close_connection(ws)
        await chunk_callback('finished', '')


def getAliyunTTSToken(apikey):
     # 获取阿里语音合成CosyVoice大模型的临时token，有效时间1800秒
    url = "https://dashscope.aliyuncs.com/api/v1/tokens?expire_in_seconds=1800"
    CosyVoice_token = cache.get('CosyVoice_token')
    if CosyVoice_token: 
        return CosyVoice_token
    else:
        req = urllib.request.Request(url,data={})
        req.add_header('Authorization', apikey)
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            obj = json.loads(content)
            cache.set('CosyVoice_token', obj['token'], 1780*60)
            return obj['token']