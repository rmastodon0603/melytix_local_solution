import json

path = 'result.json'
ga_sessions = []

with open(path, 'r') as f:
    data = json.loads(f.read())
    for element in range(len(data['ga_sessions'])):
    	ga_sessions.append(data['ga_sessions'][element])
    	#print(data['ga_sessions'][element])
    	print("GA Session in day: " + str(data['ga_sessions'][element]))

if ga_sessions[0] >= ga_sessions[1]:
	print("Hey, your traffic is good!")
else:
	print("Hey, your traffic is down!")


