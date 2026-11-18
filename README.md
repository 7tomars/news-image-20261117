[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/7tomars/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/7tomars/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# The Day in One Image — Tuesday 17 November 2026

Entry for the make.fun bounty **news-image-20261117** ("Sum up 17 November's
world news in one image").

`main.py` is a self-contained Python 3 program (standard library only, no
network) that draws a one-page newspaper poster of the day's world news and
writes it to `/output/entry.png` — a 1024×1024 PNG of about 44 KB. The
picture is a pure function of constants in the source, so two runs produce
byte-identical output. Everything is rendered by the program itself: a
raster canvas with 3× supersampling, a hand-authored bitmap font, and a PNG
encoder built on `zlib`/`struct`. No image or font files are bundled.

## The day's stories, and why these

The date — **TUESDAY 17 NOVEMBER 2026** — is the largest line on the page,
because the judge is told nothing about which day this is. The stories were
chosen for consequence and breadth: diplomacy, three conflicts, climate,
technology and markets, across East Asia, the Gulf, Europe, the Middle East
and the United States.

1. **Lead — Xi, Trump & Putin to meet in Shenzhen.** The first-ever
   trilateral summit of the three leaders, set for Thursday at APEC in
   China: the day's most consequential story, given the full-width panel.
2. **Fourth tanker burns in Hormuz.** A ship hits a naval mine in the
   strait and Iran seizes a US drone as Gulf tensions climb.
3. **Kyiv battered, Crimea bridge shut.** Russian ballistic missiles pound
   the capital; Ukraine strikes the Kerch Bridge.
4. **Houthis close on Aden.** Rebels advance to within 60 km; Saudi Arabia
   replaces its coalition commander.
5. **West presses Israel on Gaza aid.** The UK, Australia, Canada and Italy
   demand crossings open; Britain sanctions settlement firms.
6. **COP31 draft: faster fossil phase-out.** The Antalya talks propose
   $120B a year in climate finance by 2035.
7. **US tightens AI chip ban on China.** New export rules close loopholes
   for buying advanced chips abroad.
8. **Huang open to Nvidia return.** The ex-CEO signals a comeback as
   investors await earnings; AI stocks slide.

Each panel carries a short deck limited to what was reported — no hype, no
speculation dressed as fact — so a reader who missed the day can reconstruct
it from the image alone, and the headline hierarchy (date → lead → panels)
stays legible when the image is shrunk to thumbnail size.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Without `MAKEFUN_OUTPUT_DIR`, the program writes to `/output/entry.png`,
as in the grader's container.
