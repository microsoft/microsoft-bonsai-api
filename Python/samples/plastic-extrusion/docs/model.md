# Details of the Extrusion Model

## A Note on the Equations

Our mathematical model of the extrusion process below has over two dozen equations.

While GitHub can render mathematical equations in Markdown cells in [Jupyter](https://gist.github.com/cyhsutw/d5983d166fb70ff651f027b2aa56ee4e) [notebooks](https://github.com/jupyter/nbformat/blob/master/docs/markup.rst), GitHub has been [curiously](https://github.com/github/markup/issues/274) [reluctant](https://github.com/github/markup/issues/897) to include support for equations in Markdown and [reStructuredText](https://github.com/github/markup/issues/83) documents.

A [few](https://github.com/leegao/readme2tex) [workarounds](https://gist.github.com/a-rodin/fef3f543412d6e1ec5b6cf55bf197d7b) exist, but these methods lack the convenience of native support, and there is no guarantee that they will work long term.

Fortunately, Visual Studio Code has [native support for rendering equations in Markdown documents with KaTeX](https://code.visualstudio.com/updates/v1_58#_math-formula-rendering-in-the-markdown-preview), so we recommend cloning or downloading this repository to your local machine and rendering the equations with VS Code.

## Glossary

### Control Actions

- $\omega$ = screw angular speed (often denoted $N$ in literature)
- $\alpha$ = change in screw angular speed
- $\nu$ = cutter frequency (often denoted $f$)
- $\dot{\nu}$ change in cutter frequency

### Extruder Screw

- $L_s$ = length
- $D$ = diameter
- $\phi$ = helix angle
- $W$ = channel width of the melt conveying zone
- $H$ = channel depth of the melt conveying zone

### Die

- $L_d=$ length
- $R_d=$ radius
- $k=$ resistance factor (a constant that depends on the die geometry)
- $\Delta P=$ pressure drop across the die channel

### Flow Rate

- $Q=$ volumetric flow rate
- $Q_D=$ drag flow
- $Q_P=$ pressure flow
- $Q_L=$ leakage flow

### Shear Rate

- $\dot{\gamma}=$ shear rate

### Viscosity

- $m=$ consistency constant
- $n=$ power law index
- $\eta=$ viscosity

## Control Actions

The controls available to the brain are screw angular speed

$$
    \omega_{i}
        = \omega_{i-1} + \Delta t \left( \alpha_{i} + \xi_{i, \text{ screw}} \right)
$$

and cutter frequency

$$
    \nu_{i}
        = \nu_{i-1} + \Delta t \left( \dot{\nu}_i + \xi_{i, \text{ cutter}} \right)
$$

where

- $\Delta t$ is the duration of the time step (1 second in our simulation),
- $t_i$ is the current time step,
- $t_{i-1}$ is the previous time step, and
- $\xi$ represents random noise.

## Model Overview

### Flow Rate

The volumetric flow rate (i.e. material throughput) depends on several factors:

- control actions (e.g. screw angular speed),
- extruder parameters (e.g. screw diameter),
- material properties (e.g. viscosity, temperature, pressure), and
- die geometry (which determines the cross-sectional area of extruded product and the operating pressure).

### Product Length

Similarly, the product length $L$ is determined by the flow rate $Q$, the cross-sectional-area $A$ of the extruded material exiting the die, and the cutter frequency $\nu$.

$$ L = \frac{Q}{A \nu} $$

Commercial cutters for extrusion processes can use either a rotating or a vertical slicing motion.  For simplicity, we consider only vertical cutters (hence cutter frequency, rather than cutter angular velocity).

### Temperature Dependence and Other Effects

While changing the cutter frequency only affects the product length, changing the screw speed has other, secondary effects on the material properties.

For PVC extrusion, the viscosity depends primarily on shear rate and temperature.

The rotation of the screw causes the plastic pellets to agitate, creating heat and gradually melting the material.  Depending on the material being extruded, auxiliary heaters may be required to melt the material.  In some cases, however, the heat from the friction is such that fans and other cooling mechanisms are employed to keep the material at the desired temperature.

## Assumptions and Limitations

Our model of the extrusion process makes several simplifying assumptions, including:

- instantaneous response time (assume all control actions and material changes have immediate effects),
- the draw down process perfectly counteracts extrudate swell (the tendency of extruded material to expand after exiting the die), and
- the extruder is running at normal capacity (i.e. not in startup or shutdown mode).

The model also does not consider viscosity effects due to molecular weight or pressure.

Finally, certain practical considerations of operating extrusion systems are also omitted, including:

- input rate (assume the hopper feeds precisely as much material into the barrel as needed),
- dynamics from screens/breaker plates,
- coextrusion with twin screw extruders, and
- equipment wear.

## Flow Rate (Barrel)

The [volumetric flow rate](https://en.wikipedia.org/wiki/Volumetric_flow_rate) is denoted by

$$ Q \equiv \dot{V}$$

The total flow rate in an extruder is given by ([EH] eq. 3.3 and 4.2)

$$ Q = Q_D - Q_P - Q_L $$

### Drag Flow

The drag flow is ([EH] eq. 4.3)

$$ Q_D = \frac{1}{2} W H V_z $$

where $V_z$ is the plastic velocity in the channel ([EH] eq. 4.4), given by

$$ V_z = \pi D \omega \cos \phi $$

### Pressure Flow

The pressure flow ([EH] eq. 4.5) is

$$
  Q_P
    = \left( \frac{ W H^3 \sin \phi }{ 12 \, \eta } \right)
    \left( \frac{\Delta P}{\Delta L} \right)
$$

If we consider the pressure drop over the entire barrel, then $\Delta L = L_s$, and the pressure flow can be expressed as

$$
    Q_P
        = \beta_P \frac{ \Delta P }{ \eta_e }
$$

where

$$
    \beta_P
        \equiv \frac{ W H^3 \sin \phi }{ 12 \, L_s }
$$

is a constant determined by the screw parameters.

### Leakage Flow

Leakage flow is usually ignored unless the screw has excessive wear.

$$ Q_L \approx 0 $$

## Flow Rate (Die)

The volumetric flow rate in the die is given by ([EH] eq. 8.3)

$$
    Q_{die}
        = k \frac{\Delta P}{\eta}
$$

The die constant depends on the geometry, but for a circular channel ([EH] eq. 8.3),

$$ k = \frac{ \pi R_d^4 }{8 L_d} $$

The pressure drop in the channel is ([EH] eq. 8.4)

$$ \Delta P = \frac{2 L_d}{R_d} \tau $$

where $\tau=$ shear stress.

## Shear Rate (Screw Channel)

The shear rate from the rotation of the screw is ([EH] eq. 8.1)

$$
    \dot{\gamma}_s
        = \frac{ \pi D \omega }{H}
$$

## Shear Rate (Circular Die)

The shear rate in the die depends on the die geometry.  For a circular channel ([EH] eq. 8.2 and [BCP] eq. 1.4)

$$
    \dot{\gamma}_d
        = \frac{4 Q}{\pi R_d^3}
$$

## Rabinowitsch Correction

For non-Newtonian flow, the Rabinowitsch correction factor is ([BCP] eq. 1.5)

$$
    \dot{\gamma}_{\text{true}}
        = \beta_{\text{Rabinowitsch}} \dot{\gamma}_{\text{Newtonian}}
        = \left( \frac{ 3 n + 1}{4 n} \right) \left( \frac{4 Q}{\pi R^3} \right)
$$

## Polymer Viscosity

### Shear Rate

Polymers generally exhibit non-Newtonian flow behavior, and their viscosity is usually modeled with a power law ([BCP] eq. 1.2 and [D] p. 45).

$$
  \eta
    = m \dot{\gamma}^{n−1}
$$

### Temperature

The temperature dependence of viscosity is usually modeled with the [Arrhenius Equation](https://en.wikipedia.org/wiki/Arrhenius_equation) ([BCP] eq. 1.10 and [D] p. 47)

$$
  \eta
    = \eta_0
      \exp \left[
        \left( \frac{E_a}{R} \right)
        \left( \frac{1}{T} - \frac{1}{T_0} \right) \right]
$$

where

- $\eta_0$ is the viscosity at the reference temperature,
- $E_a$ is the activation energy ($85 \, \text{kJ/mol}$ for PVC),
- $R$ is the [molar gas constant](https://en.wikipedia.org/wiki/Gas_constant) ($8.314 \, J \cdot K^{-1} \cdot \text{mol}^{-1}$),
- $T$ is the temperature at the current time step, and
- $T_0$ is the reference temperature (from the previous time step).

### Linking Screw Speed and Temperature

Recall from the overview that the rotation of the screw agitates the material, which creates heat.  Table 23.1 in [EH] (reproduced below) gives approximate temperature changes associated with changes in screw angular speed for rigid PVC.

| Size Change | Screw Speed (RPM) | Temperature Change (F) |
| ----------- | ----------------- | ---------------------- |
| Small       | 1-2               | 2-4                    |
| Medium      | 10-15             | 10-15                  |
| Large       | 25+               | 30                     |

[Interpolating these values](../sim/temperature.py) links changes in screw speed to corresponding changes in temperature.

$$
  T
    = T_0 + f \left( \Delta \omega \right)
$$

### Summary

In summary, to calculate the polymer viscosity at the new temperature:

1. Determine the temperature at the new time step from the change in screw speed.
2. Calculate the viscosity due to the shear rate at the reference temperature (the previous time step).
3. Multiply by the temperature component from the Arrhenius equation.

## Operating Point

The intersection of the flow rate curves for the extruder and the die gives operating point

$$
    \left. Q_{extruder} \right|_{ P = P_{op} }
        = \left. Q_{die} \right|_{ P = P_{op} }
        \equiv Q_{op}
$$

where

$$
    Q_{extruder}
        = Q_D \left( \omega \right)
            - Q_P \left( \Delta P, \eta_e \right)
$$

and

$$
    Q_{die}
        = k \frac{ \Delta P }{ \eta_d }
$$

where $k$ is the die constant, determined from the geometry of the die.

Solving the flow rate equation for the operating pressure $P_{op}$ yields

$$
    P_{op}
        = \frac{ Q_D }{ \frac{\beta_P}{\eta_e} + \frac{k}{\eta_d}}
$$

The flow rate of the material exiting the die is then

$$
    Q_{die}
        = \frac{ k}{ \eta_d } P_{op}
        = \left( \frac{1}{1 + \zeta} \right) Q_D
$$

where

$$
    \zeta
        \equiv \left( \frac{\beta_P}{k} \right)
            \left( \frac{\eta_d}{\eta_e}\right)
$$
