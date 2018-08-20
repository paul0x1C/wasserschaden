import time, os


valves = [  3263318650, #1
            3256140760, #2
            3943574393, #3
            2485891313,
            3263314689,
            3943575913,
            3263315296,
            3954288066,
            3943574364,
            3263316235, #9
            ]

open_time = 0.2
delay = 0
cycle_delay = 0

log = []

def set(valve_id, state):
    log.append({})
    log[-1][valve_id] = state
    if state:
        print("opening %s" % (valve_id))
        os.system("""mosquitto_pub -t "painlessMesh/to/%s" -m "open" """ % valve_id)
    else:
        print("closing %s" % (valve_id))
        os.system("""mosquitto_pub -t "painlessMesh/to/%s" -m "close" """ % valve_id)


while True:
    for valve in valves:
        set(valve, 1)
        time.sleep(open_time)
        set(valve, 0)
        time.sleep(delay)
    time.sleep(cycle_delay)
