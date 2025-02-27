# Double Pendulum Simulator

A real-time double pendulum physics simulator that runs in your web browser using PyScript.

## Description

This simulator demonstrates the chaotic behavior of a double pendulum system. A double pendulum consists of two rods connected end-to-end, with a bob at the end of each rod. Despite being a simple physical system with just two degrees of freedom, the double pendulum exhibits complex chaotic motion that is highly sensitive to initial conditions.

## Features

- Real-time simulation with accurate physics
- Interactive controls for starting angles and simulation duration
- Play/Pause and Restart functionality
- Visual tracking of the distal tip's path
- Ability to toggle the trail display
- Time elapsed counter

## Usage

### Running the Simulator Locally

1. Clone this repository or download the files.
2. Open the `index.html` file in a modern web browser (Chrome, Firefox, Edge, Safari).
3. No additional installation or server setup is required!

### Controls

- **First Pendulum Angle (θ₁)**: Set the initial angle of the first pendulum (in degrees)
- **Second Pendulum Angle (θ₂)**: Set the initial angle of the second pendulum (in degrees)
- **Simulation Length**: Set how long the simulation should run (in seconds)
- **Show Trail**: Toggle to show or hide the path of the second pendulum's tip
- **Play/Pause Button**: Start or pause the simulation
- **Restart Button**: Reset the simulation with the current parameter values

### Embedding in a Webpage

To embed this simulator in your own webpage, use an iframe:

```html
<iframe src="path/to/index.html" width="100%" height="700px" frameborder="0"></iframe>
```

## Technical Details

This simulator uses:
- PyScript to run Python code in the browser
- HTML5 Canvas for rendering
- 4th-order Runge-Kutta method for numerical integration
- Standard double pendulum equations of motion

## Browser Compatibility

The simulator works best in modern browsers with good JavaScript and WebAssembly support:
- Chrome/Chromium (version 89+)
- Firefox (version 87+)
- Edge (version 89+)
- Safari (version 14.1+)

## License

This project is free to use and modify.

---

Enjoy exploring the chaotic nature of the double pendulum system!