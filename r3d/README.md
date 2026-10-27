# r3d — 3D 클레이 지도 렌더러 (The Map Answer v3, 템플릿)

**새 영상 = `../videos/<id>.json` 하나 작성** (대본·지역·나라·카메라 샷·강조·배지·라벨·소품·효과음). 코드 수정 불필요.

| 파일 | 역할 |
|---|---|
| make.sh | `sh make.sh <영상설정.json> <작업폴더> [음성폴더]` → 작업폴더/out.mp4 |
| prep3d.py | 고도(AWS Terrain Tiles, float) · 나라 ID · 육지 마스크 → data/ |
| audio3d.py | 음성(폴더 or Kokoro) + BGM + 효과음 + 덕킹 + -14 LUFS, Whisper 단어 타이밍 반영. BGM = 설정 `bgm`(이름, `../audio/bgm/catalog.json` 10곡 · 없으면 `mood`), Kevin MacLeod CC BY — **설명란 출처 줄 필수**(precheck 가 찍음), 무거운 소재에 tone light 금지(precheck). 효과음 = `../audio/sfx/*.ogg`(BigSoundBank·Kenney CC0) — 소품 종류별 자동(PROP_SFX, 끄기 `prop_sfx:false`) + 설정 `sfx: [[장면, 초, 이름(, 길이)]]`. 목록 `../audio/CREDITS.md`. `tail` 끝 무음 |
| index.html | 장면·카메라·강조·자막/배지/라벨 오버레이 (`window.frame(t)`) |
| props.js | 소품 라이브러리: drive(자동차+궤적) · trace(윤곽 그리기) · qmark · houses · ship · crest(능선 빛) · army(행진·전투·후퇴) · clash(총구 섬광·연기) · flagswap · flags · sheep · pen(국경 긋기). 새 연출은 type 추가 |
| precheck.py | **렌더 전 점검** `python3 precheck.py ../videos/<id>.json [../voice/<NNN_id>]` — 길이 35~40초·0초 큰 글자·4초 안 전환·5초 안 첫 답. 음성 없이 = 대본 단계 추정(±2초), 음성 있으면 audio3d 와 같은 계산(실제 영상과 ±0.1초) |
| render.js | `CHROME=<chromium 경로> node render.js out.mp4 30` / 정지컷 `node render.js x 30 1.5,14` |

음성: `../tts/` — Chatterbox(MIT)는 세션에서 HuggingFace 차단이라 GitHub Actions(`channel-tts.yml`)에서 생성.
`tts/job.json` 에 {configs, lines} 적고 `channel-tts-run` 브랜치로 푸시 → `channel-out` 브랜치에 wav + words.json(단어 타이밍) + check.txt(받아쓰기 대조).
준비(작업폴더): `npm i three@0.169.0 playwright @fontsource/archivo-black @fontsource/inter`, world50.json, models/(Kokoro, 폴백용).

긴 렌더(고급 룩 프레임당 ~7초): `node render.js frames 30 0 600 & node render.js frames 30 600` (중단돼도 다시 실행하면 이어서) →
`ffmpeg -framerate 30 -i frames/%05d.jpg -i final_audio.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`
