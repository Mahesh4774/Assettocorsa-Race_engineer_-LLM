import json
import ollama
# Import sector_time directly from telemetry.py!
from telemetry import sector_time

OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"


def run_driving_coach(user_prompt):
  print("\n[AGENT]: Running sector analysis from telemetry.py...")

  sector_results = sector_time()


  # Attach the corner notes to each sector and simplify the numbers
  with open("sector_notes.json", "r", encoding="utf-8") as f:
    notes = json.load(f)

  for s in sector_results:
      delta = float(s.pop("sector delta"))
      s["seconds"] = round(abs(delta), 3)   # always positive, status tells direction
      s.pop("cumulative delta", None)
      s["corner_notes"] = notes.get(str(s["id"]), {}).get("notes", "") or "none provided"
  order = {"TIME LOST": 0, "TIME GAINED": 1, "EQUAL": 2}
  sector_results.sort(key=lambda s: (order[s["status"]], -s["seconds"]))


  system_instructions = """You are a GT3 race engineer debriefing a driver after a Nordschleife lap.

Each sector has a status, seconds lost/gained, corner_notes, and speed stats:
- delta_min_kph: difference in minimum speed vs reference (negative = slower through apex/lowest point)
- delta_max_kph: difference in top speed vs reference
- delta_avg_kph: difference in average speed vs reference

RULES:
1. Write exactly one line for each of the 18 sectors, in the order provided.
2. Format: <id>. <name> - <status word> <seconds>s: <tip>
3. For TIME LOST sectors, use corner_notes AND speed deltas to diagnose the issue.
   If delta_min_kph is notably negative, the driver is likely losing speed at the apex/braking point.
   If delta_avg_kph is negative but delta_min is close, likely a carry-speed or exit issue.
   Word it as a possibility ("likely", "check whether"), never as fact.
4. For TIME GAINED sectors, reference what the speed data shows they did well.
5. 20 to 30 words per tip. Do NOT invent details not supported by corner_notes or speed data.
6. If corner_notes is "none provided", rely on speed deltas alone for a general tip.
7. Do NOT write a summary or any extra sections after the 18 lines.
Be direct and crisp."""

  full_prompt = (
      f"User Query: {user_prompt}\n\n"
      f"Sector Data:\n{json.dumps(sector_results, indent=2, ensure_ascii=False)}"
  )

  print("[AGENT]: Sending sector data to Qwen for coaching analysis...\n")

  response = ollama.chat(
      model=OLLAMA_MODEL,
      options={'temperature': 0.0,
               'top_p': 0.1,
               'num_ctx': 8192},
      messages=[
          {"role": "system", "content": system_instructions},
          {"role": "user", "content": full_prompt},
      ],
  )

  print("=== AI DRIVING COACH REPORT ===")
  print(response["message"]["content"])


if __name__ == "__main__":
  user_query = (
      "Give me a breakdown of my lap. Where did I bleed the most time?"
  )
  run_driving_coach(user_query)