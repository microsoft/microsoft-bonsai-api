# Simulator Recommendations

![](../img/sim.png)

- Simulators must be able to take a "step" or "iteration" sequentially so RL can learn to maximize the future expected return.
- Observations contain information from the result of the sim step, which can be used to calculate the state.
- Control frequency should match real life
- Should validate the simulator before expecting good results with RL
- Need to be able to convert observations and actions to Python or C++
- Minimize computation time as much as possible
