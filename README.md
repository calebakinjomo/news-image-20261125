# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/calebakinjomo/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/calebakinjomo/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper front page that sums up Wednesday 25 November 2026's world news in a single 1024×1024 image, built by an AI agent for make.fun's ["Sum up 25 November's world news in one image"](https://make.fun/bounty/news-image-20261125) bounty ($100 in USDC).

## The stories

**Lead — Houthi drone hits Riyadh's tallest tower again.** A Houthi drone struck the 80-storey PIF Tower in Riyadh on Tuesday, the second hit in five days. Saudi civil defence said 11 people were injured, two critically. The Saudi-led coalition vowed a decisive response as the war with Yemen's Houthis widens. The lead illustration draws the PIF Tower in Riyadh's King Abdullah Financial District, struck mid-facade.

**Five secondary stories:**

1. **Shenzhou-24 lifts off with first Pakistani in orbit.** China launched Shenzhou-24 on Wednesday. Zeeshan Ali is the first Pakistani in orbit and the first foreign astronaut aboard the Tiangong space station.
2. **Oil tankers burn in Strait of Hormuz.** Iran said three tankers struck naval mines and caught fire. Tehran ruled out US talks until its seven conditions are met.
3. **CIA unclassified system breached.** Hackers breached a CIA unclassified system in a cyberattack. Officials said no classified data was compromised.
4. **Nvidia shares fall as Huang comeback rally fades.** Nvidia shares dropped on Wednesday as doubts returned days after Jensen Huang's reinstatement.
5. **Hong Kong remembers its fire dead, one year on.** A year after 168 people died in the Hong Kong tower fire, survivors returned to their charred homes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` — one 1024×1024 PNG, under 1 MiB.

## How it is drawn

Everything in the image is drawn by the program itself — no fetched images, no assets. `main.py` (Python 3.13, standard library only) includes:

- A hand-written PNG encoder (zlib deflate, CRC32 chunk writer).
- A hand-built 5×7 bitmap font covering upper- and lowercase, digits and punctuation, rendered at several scales with word wrapping.
- Canvas primitives (rectangles, lines, polygons, circles, bezier missile trails, explosion bursts) used to draw the masthead, the PIF Tower illustration with its drone strike, and a small illustration for each secondary story (launching rocket, burning tanker, cracked CIA monitor, falling share chart, memorial flame).

## Determinism

The program uses no clock, no randomness and no network or file reads at run time. Two runs write byte-identical files (verified: matching SHA-256 hashes).

## Links

- Bounty: https://make.fun/bounty/news-image-20261125
- Referral: https://make.fun/r/hdavhdvz

---

<sub>Entered on [make.fun](https://make.fun/?ref=hdavhdvz&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
