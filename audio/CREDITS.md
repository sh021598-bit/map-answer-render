# 음원 출처

## BGM — Kevin MacLeod (incompetech.com), CC BY 4.0
영상 설명란에 이 줄을 넣는다(곡 이름만 바꿈):
`Music: "<곡>" Kevin MacLeod (incompetech.com) · Licensed under Creative Commons: By Attribution 4.0 · http://creativecommons.org/licenses/by/4.0/`

설정 `"bgm": "<이름>"` (없으면 `mood` 이름). 목록·tone 은 `bgm/catalog.json` — 무거운 소재엔 tone light 금지(precheck).

| 이름 | 곡 | mood | tone | 쓰임 |
|---|---|---|---|---|
| epic | Impact Lento | epic | neutral | 기본 · 역사 거래·지리 수수께끼 일반 |
| stormfront | Stormfront | epic | serious | 전쟁·제국·큰 충돌 |
| tense | Constance | tense | serious | 위협·분쟁·추격 |
| egmont | Variation on Egmont | tense | serious | 침공·전투·급박한 사건 |
| mystery | Thunder Dreams | mystery | serious | 숨은 이유·이상한 국경 |
| opium | Opium | mystery | neutral | 가벼운 수수께끼·자연 지리 |
| anguish | Anguish | somber | serious | 학살·기근·재난·잃은 땅 |
| bright | Rollin at 5 - electronic | bright | light | 거래 성공·반전·재미있는 사실 |
| evening | Evening | bright | light | 평화로운 지리·여행 |
| mississippi | Whiskey on the Mississippi | bright | light | 미국 개척·가벼운 미국사 |

## 효과음 — Kenney (kenney.nl), CC0 (출처 표기 불필요)
- coins.ogg ← rpg-audio/handleCoins.ogg
- cloth.ogg ← rpg-audio/cloth1.ogg
- pluck.ogg ← interface-sounds/pluck_001.ogg
- scratch.ogg ← interface-sounds/scratch_001.ogg
- impact.ogg ← impact-sounds/impactSoft_heavy_000.ogg

## 효과음 — BigSoundBank (Joseph SARDIN, bigsoundbank.com), CC0 (출처 표기 불필요) · 실제 녹음, 최대 음량 -1dB 로 맞춤
- gunshot.ogg ← Rifle: Shot #1 (https://bigsoundbank.com/rifle-shot-1-s2853.html)
- gunshot_2.ogg ← Rifle: Shot #2 (https://bigsoundbank.com/rifle-shot-2-s2854.html)
- cannon.ogg ← Explosion far Away #1 (https://bigsoundbank.com/explosion-far-away-s1023.html)
- explosion.ogg ← Explosion far Away #1 (https://bigsoundbank.com/explosion-far-away-s1023.html)
- applause.ogg ← Shouts and Applauses of Teens #2 — **축하(독립·조약 성공)만, 전쟁 장면 금지**(precheck 가 막음). 전쟁 함성 녹음은 CC0 에서 못 찾아 없음 (https://bigsoundbank.com/shouts-and-applauses-of-teens-2-s0237.html)
- splash.ogg ← Splash, Small #1 (https://bigsoundbank.com/splash-small-1-s1529.html)
- splash_2.ogg ← Splash, Big #3 (https://bigsoundbank.com/splash-big-3-s1521.html)
- waves.ogg ← Small Waves Facing the Ocean (https://bigsoundbank.com/small-waves-facing-the-ocean-s1046.html)
- sheep.ogg ← Sheep #1 (https://bigsoundbank.com/sheep-1-s2343.html)
- sheep_2.ogg ← Sheep #6 (https://bigsoundbank.com/sheep-6-s2348.html)
- car.ogg ← Car, Starting and Departure (https://bigsoundbank.com/car-starting-and-departure-s0189.html)
- horn.ogg ← Ocean Liner Horn #1 (https://bigsoundbank.com/horn-of-a-ship-1-s0261.html)
- wind.ogg ← Wind (https://bigsoundbank.com/wind-s0595.html)
- glass.ogg ← Cheers, Champagne Flute #1 (https://bigsoundbank.com/cheers-champagne-flute-1-s1335.html)
- horse.ogg ← Horse Gallop (https://bigsoundbank.com/horse-gallop-s0611.html)
- bell.ogg ← Church Bell (https://bigsoundbank.com/church-bell-s0135.html)
- march.ogg ← Footsteps on gravels #1 3겹 (https://bigsoundbank.com/steps-on-gravels-s0510.html)

## 자동 연결 (audio3d PROP_SFX)
- coins·nuggets→coins · flags·flagswap→cloth · qmark·pricetag·dateline·span·houses→pluck · trace·pen→scratch · glasses→glass · sheep→sheep · army(행진 구간)→march · clash→gunshot 여러 발 · ship→waves · swimmer·otters→splash · drive→car · 장면 전환→impact
- 그 밖의 장면(대포·폭발·박수(축하만)·종·말·뱃고동·바람)은 설정 `"sfx": [[장면, 초, "이름"(, 길이)]]` 로 직접.
