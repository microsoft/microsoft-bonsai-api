from flask import Flask, request
import json 

class Adder:
    """
    Add numbers to a running total.
    This is a placeholder for a simulation that, in a real solution, would be much more complicated.
    """

    def __init__(self, initial_value: float):
        self.value = initial_value

    def add(self, addend: float):
        self.value += addend


# Setup flask server
app = Flask(__name__) 
  
# Setup url route which will calculate
# total sum of array.
@app.route('/sim_reset', methods = ['POST']) 
def sim_reset(): 
    data = request.get_json() 
    print("flask reset:", data)
    simModel = Adder(data['initial_value'])
    return json.dumps({"value":simModel.value})

@app.route('/sim_step', methods = ['POST']) 
def sim_step(): 
    data = request.get_json() 
    print("flask step:", data)
    simModel.add(data['addend'])
    return json.dumps({"value":simModel.value})

if __name__ == "__main__": 
    app.run(port=15000)
    simModel = Adder(1.0)