import json
import ollama
import time
# Import sector_time directly from race_telemetry.py
from race_telemetry import sector_time

OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"

MIN_LOSS_S = 0.05
MAX_SECTORS = 8

def run_driving_coach(user_prompt):
  print("\n[AGENT]: Running sector analysis from telemetry.py...")
  sector_results = sector_time()

  # Attach the corner notes to each sector and simplify the numbers
  with open("sector_notes.json", "r", encoding="utf-8") as f:
    notes = json.load(f)
  lost = []
  for s in sector_results:
      if s["status"] != "TIME LOST":
          continue
      seconds = round(float(s["sector delta"]),3)
      if seconds < MIN_LOSS_S:
          continue
      spd = s["speed"]
      lost.append({
          "id":s["id"],
          "name":s["name"],
          "seconds_lost":seconds,
          "delta_min_kph": round(spd["min_speed_delta_kph"], 1),
          "delta_max_kph": round(spd["max_speed_delta_kph"], 1),
          "delta_avg_kph": round(spd["avg_speed_delta_kph"], 1),
          "corner_notes": notes.get(str(s["id"]), {}).get("notes", "") or "none provided",
      })

      lost.sort(key=lambda s: s["seconds_lost"], reverse=True)
      if MAX_SECTORS:
          lost = lost[:MAX_SECTORS]
      if not lost:
          print("No meaningful time lost in any sector.")
          return


  system_instructions = """You are a GT3 race engineer debriefing a driver after a Nordschleife lap.

You are given the sectors where the driver lost the most time, worst first.
Each has seconds_lost, corner_notes, and speed deltas vs the reference lap:
- delta_min_kph: negative = slower at the apex/lowest point
- delta_max_kph: negative = lower top speed
- delta_avg_kph: negative = slower on average through the sector

RULES:
1. Write exactly one line per sector, in the order provided.
2. Format: <id>. <name> - lost <seconds_lost>s: <tip>
3. Use corner_notes AND the speed deltas to diagnose the issue.
   If delta_min_kph is notably negative, the driver is likely losing speed at the apex/braking point.
   If delta_avg_kph is negative but delta_min_kph is close, likely a carry-speed or exit issue.
   Word it as a possibility ("likely", "check whether"), never as fact.
4. 10 to 15 words per tip. Do NOT invent details not in corner_notes or the speed data.
5. If corner_notes is "none provided", rely on the speed deltas alone.
6. No summary or extra text after the lines.
Be direct and crisp."""

  full_prompt = (
      f"User Query: {user_prompt}\n\n"
      f"Sector Data:\n{json.dumps(lost, indent=2, ensure_ascii=False)}"
  )

  print("[AGENT]: Sending sector data to Qwen for coaching analysis...\n")

  t1 = time.time()
  print(f"[DEBUG] sectors sent: {len(lost)}")


  stream = ollama.chat(
      model=OLLAMA_MODEL,
      options={'temperature': 0.0,
               'top_p': 0.1,
               'num_ctx': 8192},
      messages=[
          {"role": "system", "content": system_instructions},
          {"role": "user", "content": full_prompt},
      ],
      stream=True
  )


  print("=== AI DRIVING COACH REPORT ===")


  last = None
  for chunk in stream:
      print(chunk["message"]["content"], end="", flush=True)
      last = chunk
  print()

  print(f"[TIMER] LLM: {time.time() - t1:.1f}s")
  print(f"load:        {last['load_duration'] / 1e9:.1f}s")
  print(f"prompt eval: {last['prompt_eval_duration'] / 1e9:.1f}s  ({last['prompt_eval_count']} tokens)")
  print(f"generation:  {last['eval_duration'] / 1e9:.1f}s  ({last['eval_count']} tokens)")

if __name__ == "__main__":
  user_query = (
      "Give me a breakdown of my lap. Where did I bleed the most time?"
  )
  run_driving_coach(user_query)