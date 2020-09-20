import json

path = 'result.json'
ga_sessions = []

with open(path, 'r') as f:
    data = json.loads(f.read())
    for element in range(len(data['ga_sessions'])):
       	ga_sessions[element] = data['ga_sessions'][element]

for i in ga_sessions:
	print(i)
