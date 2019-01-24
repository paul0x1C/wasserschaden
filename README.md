# wasserschaden
Project to control solenoid valves over mqtt, check each nodes status in a webpage and via Grafana. 
It allows you to set a location for each node that connects for the first time for easier maintenance.
Nodes equipped with a temperature sensor also send temperature information via mqtt.
To prevent two solenoid valves opening simultaniously, a house enters "locked state". Before opening a solenoid valve,
it checks the lockstate of its house and will only open if the house is in unlocked state.
We log every opening and closing of a valve in order to be able to generate a csv log file, to prove reliability.
