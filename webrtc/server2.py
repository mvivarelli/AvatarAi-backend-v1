import asyncio
import json
import logging
import os
import uuid

import cv2
from aiohttp import web
from av import VideoFrame
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceServer, RTCConfiguration
from aiortc.contrib.media import MediaPlayer

ROOT = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webrtc")
pcs = set()


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, transform):
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        transformations = {
            "cartoon": self._apply_cartoon,
            "edges": self._apply_edges,
            "rotate": self._apply_rotate,
        }

        if self.transform in transformations:
            img = transformations[self.transform](img, frame)

        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame

    def _apply_cartoon(self, img, frame):
        img_color = cv2.pyrDown(cv2.pyrDown(img))
        for _ in range(6):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
        img_color = cv2.pyrUp(cv2.pyrUp(img_color))
        img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img_edges = cv2.adaptiveThreshold(
            cv2.medianBlur(img_edges, 7),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)
        return cv2.bitwise_and(img_color, img_edges)

    def _apply_edges(self, img, frame):
        return cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

    def _apply_rotate(self, img, frame):
        rows, cols, _ = img.shape
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
        return cv2.warpAffine(img, M, (cols, rows))


async def index(request):
    return web.FileResponse(os.path.join(ROOT, "index2.html"))


async def javascript(request):
    return web.FileResponse(os.path.join(ROOT, "client2.js"))


async def offer(request):
    try:
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        transform = params.get("video_transform", "none")
    except (json.JSONDecodeError, KeyError):
        return web.Response(status=400, text="Invalid JSON payload")

    ice_servers = [
        RTCIceServer(urls="stun:stun.relay.metered.ca:80"),
        RTCIceServer(urls="turn:global.relay.metered.ca:80", username="6c82d60fa1c26ed4b63f8c67", credential="14Bn1nyBcAQyDehx"),
        RTCIceServer(urls="turn:global.relay.metered.ca:80?transport=tcp", username="6c82d60fa1c26ed4b63f8c67", credential="14Bn1nyBcAQyDehx"),
        RTCIceServer(urls="turn:global.relay.metered.ca:443", username="6c82d60fa1c26ed4b63f8c67", credential="14Bn1nyBcAQyDehx"),
        RTCIceServer(urls="turns:global.relay.metered.ca:443?transport=tcp", username="6c82d60fa1c26ed4b63f8c67", credential="14Bn1nyBcAQyDehx")
    ]
    ice_transport_policy = 'all'
    
    # pc = RTCPeerConnection(iceServers=ice_servers, iceTransportPolicy=ice_transport_policy)
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=ice_servers))
    # pc = RTCPeerConnection()
    
    pc_id = f"PeerConnection({uuid.uuid4()})"
    pcs.add(pc)
    logger.info("Created %s for %s", pc_id, request.remote)

    player = MediaPlayer(os.path.join(ROOT, "ok-low.mp4"))
    # player = MediaPlayer(os.path.join(ROOT, "../SadTalker/output.mp4"))
    pc.addTrack(VideoTransformTrack(player.video, transform))
    pc.addTrack(player.audio)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("%s state changed to %s", pc_id, pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})


async def on_shutdown(app):
    await asyncio.gather(*[pc.close() for pc in pcs])
    pcs.clear()


if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_routes([
        web.get("/", index),
        web.get("/client2.js", javascript),
        web.post("/offer", offer),
    ])
    web.run_app(app, host="0.0.0.0", port=5020)
