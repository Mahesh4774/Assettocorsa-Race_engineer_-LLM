import json
import matplotlib.pyplot as plt
import numpy as np

JSON_FILE = "1790271064-Moota47-2(426.94)_nordschleife.json"

with open(JSON_FILE, "r") as d:
  data = json.load(d)

def format_laptime(seconds):
    minutes = int(seconds // 60)
    remainder_seconds = seconds % 60
    secs = int(remainder_seconds)
    milliseconds = int(round((remainder_seconds - secs) * 1000))

    # Handle rounding edge case where ms rounds up to 1000
    if milliseconds >= 1000:
        secs += 1
        milliseconds -= 1000
        if secs >= 60:
            minutes += 1
            secs -= 60

    return f"{minutes} min {secs} seconds, {milliseconds} ms"
def process_lap(lap_key, laptime_index):

    track_distance = np.array(data["laps"][lap_key]["lapdistance"])
    speed = np.array(data["laps"][lap_key]["speed"])
    min_lenght = min(len(track_distance),len(speed))
    track_distance = track_distance[:min_lenght]
    speed = speed[:min_lenght]

    official_laptime = data["laptimes"][laptime_index]
    sample_rate = 1.0 / data["dataRate"]
    time_array = np.arange(len(track_distance)) * sample_rate

    if time_array[-1] > 0:
        time_array = time_array * (official_laptime / time_array[-1])

    return track_distance, time_array, speed


def sector_time():

    sorted_laps = sorted(enumerate(data["laptimes"]), key=lambda x: x[1])

    ref_idx, ref_time = sorted_laps[0]
    target_lap_idx, target_lap_time = sorted_laps[1]

    dist_ref, time_ref, speed_ref = process_lap(str(ref_idx + 1), ref_idx)
    dist_curr, time_curr, speed_curr = process_lap(str(target_lap_idx + 1), target_lap_idx)

    print(f"dist_ref: {len(dist_ref)}, speed_ref: {len(speed_ref)}")
    print(f"dist_curr: {len(dist_curr)}, speed_curr: {len(speed_curr)}")

    min_distance = min(dist_ref[-1], dist_curr[-1])
    distance_grid = np.arange(0, min_distance, 1.0)

    ref_laptime_interp = np.interp(distance_grid, dist_ref, time_ref)
    current_laptime_interp = np.interp(distance_grid, dist_curr, time_curr)

    # speed mapped to the same distance grid
    ref_speed_interp = np.interp(distance_grid, dist_ref, speed_ref)
    curr_speed_interp = np.interp(distance_grid, dist_curr, speed_curr)



    time_delta = current_laptime_interp - ref_laptime_interp

    with open("nordschleife_sectors.json", "r", encoding="utf-8") as s:
        sector_load = json.load(s)
    grid_max = len(distance_grid) - 1
    sector_details = []

    for sector in sector_load["sectors"]:
        sector_start = min(int(sector["start_m"]), grid_max)
        sector_end = min(int(sector["end_m"]), grid_max)

        ref_slice = ref_speed_interp[sector_start:sector_end]
        curr_slice = curr_speed_interp[sector_start:sector_end]

        speed_data = {
            "current_min_speed_kph" : float(curr_slice.min()),
            "current_max_speed_kph" : float(curr_slice.max()),
            "current_avg_speed_kph" : float(curr_slice.mean()),
            "min_speed_delta_kph" : float(curr_slice.min() - ref_slice.min()),
            "max_speed_delta_kph" : float(curr_slice.max() - ref_slice.max()),
            "avg_speed_delta_kph" : float(curr_slice.mean() - ref_slice.mean())
        }

        sector_delta = time_delta[sector_end] - time_delta[sector_start]
        if sector_delta < 0:
            status = "TIME GAINED"
        elif sector_delta > 0:
            status = "TIME LOST"
        else:
            status = "EQUAL"
        cumulative_delta = time_delta[sector_end]

        sector_details.append(
            {
                "id": sector["sector_id"],
                "name": sector["name"],
                "sector delta": sector_delta,
                "status":status,
                "cumulative delta": cumulative_delta,
                "speed" : speed_data
            }
        )
        # For printing in console
    print(f"Reference Lap Time: {format_laptime(ref_time)}")
    print(f"Current Lap Time:   {format_laptime(target_lap_time)}")
    print(f"Official Delta:     {target_lap_time - ref_time:>+11.3f}s")
    print(f"Calculated Delta at grid end: {time_delta[-1]:.3f}s\n")
    print(f"{'ID':<3} | {'Sector Name':<38} | {'Sector Delta':<12} | {'Status':<12} | {'Cumulative':<10} | "
          f"{'Avg_Speed':<10} |{'dAvg_Speed':<10} | {'dMin_Speed':<10} | {'dMax_Speed':<10}")
    print("-" * 140)

    for s in sector_details:
        spd = s["speed"]
        print(
            f"{s['id']:<3} | {s['name']:<38} | {s['sector delta']:>+11.3f}s | {s['status']:<12} |"
            f" {s['cumulative delta']:>+9.3f}s |" 
            f"{spd['current_avg_speed_kph']:>11.3f} | {spd['avg_speed_delta_kph']:>+10.3f} |"
            f"{spd['min_speed_delta_kph']:>+10.3f} | {spd['max_speed_delta_kph']:>+10.3f} |"
        )

    return sector_details

if __name__ == "__main__":
    sector_time()


# PLOTTING ON GRAPH

# plt.figure(figsize=(12,5))
# plt.plot(track_distance,current_speed)
# plt.xlabel("Track Distande (m)")
# plt.ylabel("Speed (kph)")
# plt.title("Speed vs Track Distance")
# plt.grid(True)
# plt.show() 

# print(len(track_distance))
# print(len(throttle_values))
# print(len(brake_values))
# print(len(current_speed))
# print(len(current_gear))
# print(len(current_rpm))
# print(lap_distance_covered)
# print(len(pos_x))
# print(len(pos_y))
# print(len(steering_input))

# track_distance = lap["trackdistance"]
# throttle_values = lap["throttle"]
# brake_values = lap["brake"]
# current_speed = lap["speed"]
# current_gear = lap["gear"]
# current_rpm = lap["rpm"]
# lap_distance_covered = lap["lapdistance"]
# pos_x = lap["posx"]
# pos_y = lap["posy"]
# steering_input = lap["steer"]

