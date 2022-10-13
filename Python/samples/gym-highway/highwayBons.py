import gym
import highway_env
import requests
import json

env = gym.make('highway-v0')
obs = env.reset()
print("Observation:", obs)


# General variables
url = "http://localhost:5000"
predictionPath = "/v1/prediction"
headers = {
  "Content-Type": "application/json"
}
endpoint = url + predictionPath

while True:
  done = False
  obs = env.reset()
  while not done:
    print("obs: ", obs)
    v1 = [float(obs[0][0]), float(obs[0][1]), float(obs[0][2]), float(obs[0][3]), float(obs[0][4]), 0.0,0.0]
    v2 = [float(obs[1][0]), float(obs[1][1]), float(obs[1][2]), float(obs[1][3]), float(obs[1][4]), 0.0,0.0]
    v3 = [float(obs[2][0]), float(obs[2][1]), float(obs[2][2]), float(obs[2][3]), float(obs[2][4]), 0.0,0.0]
    v4 = [float(obs[3][0]), float(obs[3][1]), float(obs[3][2]), float(obs[3][3]), float(obs[3][4]), 0.0,0.0]
    v5 = [float(obs[4][0]), float(obs[4][1]), float(obs[4][2]), float(obs[4][3]), float(obs[4][4]), 0.0,0.0]
    # print("v1: ", v1)
    # print("v2: ", v2)
    # print("v3: ", v3)
    # print("v4: ", v4)
    # print("v5: ", v5)
    
    requestBody = {
      "vehicle1":  v1,
      "vehicle2":  v2,
      "vehicle3":  v3,
      "vehicle4":  v4,
      "vehicle5":  v5
    }
    
    print("requestBody: ", requestBody)

# Send the POST request
    response = requests.post(
                endpoint,
                data = json.dumps(requestBody),
                headers = headers
              )

    # Extract the JSON response
    prediction = response.json()
    print("prediction: ", prediction)
    action = int(prediction["steer"])
    print("action: ", action)
    obs, reward, done, info = env.step(action)
    env.render()
    
    