# LLM Race Engineer: Assetto Corsa (Nürburgring Nordschleife)

A Python tool that analyses Assetto Corsa telemetry lap by lap, finds where time is lost or gained on the Nordschleife, and uses a local LLM (via Ollama) to turn the numbers into short, sector-by-sector driving feedback, like a race engineer debrief.

I built this because I've driven thousands of kilometres on the Nordschleife in sim racing, and I wanted a tool that tells me *where* I lose time and *why*, not just how much.

## What it does

1. Loads exported telemetry for a session (laps, lap times, lap distance, speed).
2. Takes the fastest lap as the **reference** and the second fastest as the **target lap**.
3. Resamples both laps onto a common 1 m distance grid so they can be compared point by point.
4. Splits the track into **18 hand-mapped sectors** (Hatzenbach, Flugplatz, Fuchsröhre, Karussell, Pflanzgarten, Döttinger Höhe, and so on) and calculates, for each sector:
   - time lost or gained against the reference lap
   - minimum, maximum and average speed, and the difference from the reference
5. Attaches written corner notes to each sector (braking points, crests, banking, exit priorities).
6. Sends the sector data to a local LLM, which writes one line of feedback per sector, ordered from most time lost to most time gained.

The LLM is only used to explain the numbers. All timing and speed calculations are done in Python with NumPy.

## Project structure

| File | Purpose |
|---|---|
| `race_telemetry.py` | Loads the lap data, aligns two laps by distance, and computes sector deltas and speed stats |
| `race_eng_agent.py` | Builds the prompt from the sector data and corner notes, and gets the coaching report from the LLM |
| `nordschleife_sectors.json` | The 18 sector boundaries (start and end in metres, total track length 20,832 m) |
| `sector_notes.json` | Driving notes for each sector, used to give the LLM context |
| `setup_telemetry.py` | Work in progress: loads car setup channels (such as camber) from raw CSV telemetry |

## Requirements

- Python 3.10+
- NumPy, Matplotlib, pandas
- [Ollama](https://ollama.com) running locally, with the model pulled:

```bash
pip install numpy matplotlib pandas ollama
ollama pull qwen2.5:7b-instruct-q4_K_M
```

## How to run

1. Export your session telemetry as JSON and put it in the project folder.
2. Set `JSON_FILE` at the top of `race_telemetry.py` to your file name.
3. Print the sector table to check the numbers first:

```bash
python race_telemetry.py
```

4. Run the race engineer:

```bash
python race_eng_agent.py
```

## Example output

> Add a screenshot of the sector table and a copy of the coach's report here.


<img width="1783" height="749" alt="Screenshot (85)" src="https://github.com/user-attachments/assets/d524057b-754d-4578-b067-e23c73302239" />
<img width="1811" height="686" alt="Screenshot (86)" src="https://github.com/user-attachments/assets/1907816f-bd96-4d9d-9c0c-d8905a0bfdef" />



## Design choices

- **Distance-based comparison, not time-based.** Both laps are interpolated onto the same distance grid, so sectors line up even when the laps run at different speeds.
- **Check against the official lap time.** The script prints the calculated delta next to the official lap time difference to catch data problems.
- **Sector boundaries live in JSON.** They're not hardcoded, so the same approach can be reused for other tracks.
- **The LLM is constrained.** Temperature is set to 0, it must write exactly one line per sector, and it must phrase causes as possibilities ("likely", "check whether") and not as facts.

## Current limitations

- The analysis compares two laps from one session, so it shows differences between those laps and is not a full picture of driving performance.
- The time array is scaled to match the official lap time, so small errors in the raw data are absorbed by that scaling.
- LLM feedback is a set of hypotheses based on speed data and notes. It is not a measured diagnosis.

## Roadmap (v2, in progress)

- [x] Per-sector time delta and speed analysis
- [x] LLM coaching report with corner notes
- [ ] Compare **static vs dynamic camber** between two sessions with different setups, per sector
- [ ] Compare **toe** values between setups
- [ ] Add **tyre slip** (and tyre temperature) to link setup changes to results


## Tech stack

Python, NumPy, pandas, Matplotlib, Ollama (Qwen 2.5 7B), Assetto Corsa telemetry
