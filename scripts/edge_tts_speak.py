"""Synthesize one line with Microsoft Edge Read Aloud TTS.

The public `edge-tts` CLI still points at
`wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1`,
which Microsoft started refusing with HTTP 403 in many regions (including
mainland China) in late 2026. The same service is still available on
`wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1`; it accepts
the same TrustedClientToken / Sec-MS-GEC pair, with the token repeated as
`Ocp-Apim-Subscription-Key`.

This wrapper monkey-patches `edge_tts.communicate.WSS_URL` for that host and
falls back to the old host if the new one is refused.

Usage (called by ftvoice.py, not usually by hand)
-------------------------------------------------
  python scripts/edge_tts_speak.py --text "测试" \
      --voice zh-CN-XiaoxiaoNeural --rate +15% --out out.mp3
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

import edge_tts
import edge_tts.communicate as communicate
from edge_tts.constants import TRUSTED_CLIENT_TOKEN

NEW_URL = (
    "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
    f"?TrustedClientToken={TRUSTED_CLIENT_TOKEN}"
    f"&Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}"
)
OLD_URL = communicate.WSS_URL


async def synth(text: str, voice: str, rate: str, out: Path) -> int:
    """One attempt on the currently selected host. Returns audio byte count."""
    comm = edge_tts.Communicate(text, voice, rate=rate, connect_timeout=20, receive_timeout=60)
    written = 0
    with out.open("wb") as f:
        async for chunk in comm.stream():
            if chunk.get("type") == "audio" and chunk.get("data"):
                f.write(chunk["data"])
                written += len(chunk["data"])
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # The new host occasionally refuses a handshake transiently (edge-tts#490);
    # three attempts clear almost all of those. The legacy host gets one.
    attempts = (("api.msedgeservices.com", NEW_URL, 4), ("speech.platform.bing.com", OLD_URL, 1))
    errors: list[str] = []
    for label, url, tries in attempts:
        communicate.WSS_URL = url
        for i in range(tries):
            try:
                n = asyncio.run(synth(args.text, args.voice, args.rate, out))
                if n > 512:
                    print(f"edge-tts ok via {label}: {n} bytes", file=sys.stderr)
                    return 0
                errors.append(f"{label}: empty audio")
            except Exception as e:  # noqa: BLE001 - surface one clean error to the caller
                errors.append(f"{label} try {i + 1}: {e}")
            # A failed attempt's output must not be mistaken for success.
            if out.exists() and out.stat().st_size < 512:
                out.unlink(missing_ok=True)
            if i + 1 < tries:
                time.sleep(1.0)
    print(f"edge-tts failed for {args.voice}: " + " | ".join(errors[-3:]), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
