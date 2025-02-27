import numpy as np
import js
from pyodide.ffi import create_proxy
from double_pendulum import DoublePendulum
import math
import sys

# Global variables
pendulum = None
animation_id = None
running = False
max_time = 60  # Default simulation length in seconds
canvas = None
ctx = None
width = 0
height = 0
scale = 100  # Scale factor for the pendulum visualization
center_x = 0
center_y = 0
show_trail = True
keep_full_trail = False  # New option for keeping the entire trail
initialized = False  # Track if we're already initialized
last_theta1 = None   # Track last used theta1 value
last_theta2 = None   # Track last used theta2 value
last_sim_length = None  # Track last used simulation length

def log_message(message):
    """Print debug message to console"""
    js.console.log(message)

def setup_canvas():
    """Set up the canvas element and context for drawing."""
    global canvas, ctx, width, height, center_x, center_y
    
    try:
        # Get the canvas element
        log_message("Looking for canvas element...")
        canvas = js.document.getElementById("pendulum-canvas")
        if canvas is None:
            log_message("ERROR: Canvas element not found!")
            return False
            
        log_message("Getting canvas context...")
        try:
            ctx = canvas.getContext("2d")
            if ctx is None:
                log_message("ERROR: Could not get 2D context!")
                return False
        except Exception as e:
            log_message(f"ERROR getting canvas context: {str(e)}")
            return False
        
        # Set canvas dimensions
        width = canvas.width
        height = canvas.height
        log_message(f"Canvas dimensions: {width}x{height}")
        
        # Calculate center coordinates
        center_x = width / 2
        center_y = height / 3  # Position pendulum in the upper third of canvas
        
        # Draw a test rectangle to verify the canvas is working
        try:
            ctx.fillStyle = "#FF0000"
            ctx.fillRect(center_x - 50, center_y - 50, 100, 100)
            log_message("Canvas setup successful - Test rectangle drawn")
        except Exception as e:
            log_message(f"ERROR drawing test rectangle: {str(e)}")
            return False
            
        return True
    except Exception as e:
        log_message(f"ERROR setting up canvas: {str(e)}")
        return False

def hex_to_rgba(hex_color, alpha=1.0):
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def init_simulation():
    """Initialize the simulation with user input values."""
    global pendulum, running, max_time, last_theta1, last_theta2, last_sim_length, keep_full_trail
    
    try:
        log_message("Initializing simulation...")
        # Get user input values
        theta1_input = js.document.getElementById("theta1")
        theta2_input = js.document.getElementById("theta2")
        sim_length_input = js.document.getElementById("simulation-length")
        
        if theta1_input is None or theta2_input is None or sim_length_input is None:
            log_message("ERROR: Input elements not found!")
            return False
            
        theta1_deg = float(theta1_input.value)
        theta2_deg = float(theta2_input.value)
        max_time = float(sim_length_input.value)
        
        log_message(f"Input values: theta1={theta1_deg}, theta2={theta2_deg}, max_time={max_time}")
        
        # Store the current values for later comparison
        last_theta1 = theta1_deg
        last_theta2 = theta2_deg
        last_sim_length = max_time
        
        # Convert degrees to radians
        theta1_rad = math.radians(theta1_deg)
        theta2_rad = math.radians(theta2_deg)
        
        # Create pendulum object
        log_message("Creating pendulum object...")
        pendulum = DoublePendulum(theta1=theta1_rad, theta2=theta2_rad)
        
        # Update UI
        update_time_display()
        
        # Set running state
        running = False
        
        # Draw the initial state
        draw()
        
        # Set up initial trail visibility
        full_trail_container = js.document.getElementById("full-trail-container")
        if full_trail_container and show_trail:
            full_trail_container.style.display = "flex"
            
        # Automatically check the "Keep Full Trail History" checkbox
        full_trail_checkbox = js.document.getElementById("keep-full-trail")
        if full_trail_checkbox:
            full_trail_checkbox.checked = True
            keep_full_trail = True
            # Update the pendulum's trail history
            if pendulum is not None:
                log_message("Enabling unlimited trail history by default")
                pendulum.set_max_history_length(None)  # Unlimited
        
        log_message("Simulation initialized successfully")
        return True
    except Exception as e:
        log_message(f"ERROR initializing simulation: {str(e)}")
        return False

def toggle_simulation(event=None):
    """Toggle the simulation between running and paused states."""
    global running, animation_id
    
    try:
        log_message("Toggle simulation called")
        
        # Check if input values have changed
        theta1_input = js.document.getElementById("theta1")
        theta2_input = js.document.getElementById("theta2")
        sim_length_input = js.document.getElementById("simulation-length")
        
        values_changed = False
        
        if theta1_input and theta2_input and sim_length_input:
            current_theta1 = float(theta1_input.value)
            current_theta2 = float(theta2_input.value)
            current_sim_length = float(sim_length_input.value)
            
            # Check if values have changed from last used values
            if (last_theta1 is None or 
                last_theta2 is None or 
                last_sim_length is None or
                current_theta1 != last_theta1 or 
                current_theta2 != last_theta2 or
                current_sim_length != last_sim_length):
                values_changed = True
                log_message("Input values have changed, restarting simulation")
                
                # Hide the restart notice if it's showing
                restart_notice = js.document.getElementById("restart-notice")
                if restart_notice:
                    restart_notice.style.display = "none"
                    restart_notice.classList.remove("flash")
                
                # Restart the simulation with new values
                restart_simulation()
                
                # Add debug message about values changing
                js.document.getElementById("debug-output").innerHTML += '<p style="color: blue;">Values changed - Simulation restarted automatically</p>'
        
        # If simulation is not initialized, initialize it
        if pendulum is None:
            if not init_simulation():
                log_message("Failed to initialize simulation")
                return
        
        # Only toggle running state if we didn't just restart
        if not values_changed:
            # Toggle running state
            running = not running
        else:
            # Always start running after a restart
            running = True
        
        # Update button text
        play_button = js.document.getElementById("play-button")
        if running:
            log_message("Starting animation")
            play_button.textContent = "Pause"
            animation_id = js.window.requestAnimationFrame(create_proxy(animation_loop))
        else:
            log_message("Pausing animation")
            play_button.textContent = "Play/Pause"
            if animation_id is not None:
                js.window.cancelAnimationFrame(animation_id)
                animation_id = None
    except Exception as e:
        log_message(f"ERROR toggling simulation: {str(e)}")

def restart_simulation(event=None):
    """Restart the simulation with new parameters."""
    global running, animation_id, pendulum, keep_full_trail
    
    try:
        log_message("Restarting simulation")
        # Stop any running animation
        if animation_id is not None:
            js.window.cancelAnimationFrame(animation_id)
            animation_id = None
        
        # Initialize simulation with new parameters
        init_simulation()
        
        # Set running state to false
        running = False
        
        # Update button text
        play_button = js.document.getElementById("play-button")
        play_button.textContent = "Play/Pause"
        
        # Hide the restart notice
        restart_notice = js.document.getElementById("restart-notice")
        if restart_notice:
            restart_notice.style.display = "none"
            restart_notice.classList.remove("flash")
        
        # Ensure "Keep Full Trail History" remains checked
        full_trail_checkbox = js.document.getElementById("keep-full-trail")
        if full_trail_checkbox:
            full_trail_checkbox.checked = True
            keep_full_trail = True
            # Update the pendulum's trail history
            if pendulum is not None:
                log_message("Ensuring unlimited trail history on restart")
                pendulum.set_max_history_length(None)  # Unlimited
        
        # Draw initial state
        draw()
    except Exception as e:
        log_message(f"ERROR restarting simulation: {str(e)}")

def toggle_trail(event=None):
    """Toggle the visibility of the tip trail."""
    global show_trail, keep_full_trail
    
    try:
        log_message("Toggling trail visibility")
        show_trail = not show_trail
        
        # Update checkbox state
        trail_checkbox = js.document.getElementById("show-trail")
        trail_checkbox.checked = show_trail
        
        # Show or hide the full trail option based on trail visibility
        full_trail_container = js.document.getElementById("full-trail-container")
        if full_trail_container:
            if show_trail:
                full_trail_container.style.display = "flex"
                # Make sure full trail option is checked when trail is shown
                full_trail_checkbox = js.document.getElementById("keep-full-trail")
                if full_trail_checkbox:
                    full_trail_checkbox.checked = True
                    keep_full_trail = True
                    # Update the pendulum's trail history
                    if pendulum is not None:
                        log_message("Enabling unlimited trail history when trail is shown")
                        pendulum.set_max_history_length(None)  # Unlimited
            else:
                full_trail_container.style.display = "none"
        
        # Redraw
        draw()
    except Exception as e:
        log_message(f"ERROR toggling trail: {str(e)}")

def toggle_full_trail(event=None):
    """Toggle between limited and unlimited trail history."""
    global keep_full_trail
    
    try:
        log_message("Toggling full trail option")
        keep_full_trail = not keep_full_trail
        
        # Update checkbox state
        full_trail_checkbox = js.document.getElementById("keep-full-trail")
        full_trail_checkbox.checked = keep_full_trail
        
        # Update the pendulum's trail history length
        if pendulum is not None:
            if keep_full_trail:
                log_message("Enabling unlimited trail history")
                pendulum.set_max_history_length(None)  # Unlimited
            else:
                log_message("Limiting trail history to 1000 points")
                pendulum.set_max_history_length(1000)  # Default limit
        
        # Redraw
        draw()
    except Exception as e:
        log_message(f"ERROR toggling full trail: {str(e)}")

def update_time_display():
    """Update the time display in the UI."""
    try:
        if pendulum is not None:
            current_time = pendulum.get_time()
            time_display = js.document.getElementById("time-display")
            time_display.textContent = f"Time: {current_time:.2f}s / {max_time:.2f}s"
    except Exception as e:
        log_message(f"ERROR updating time display: {str(e)}")

def draw():
    """Draw the pendulum and its trail on the canvas."""
    try:
        if pendulum is None:
            log_message("Cannot draw: pendulum is None")
            return
            
        if ctx is None:
            log_message("Cannot draw: context is None")
            return
            
        if canvas is None:
            log_message("Cannot draw: canvas is None")
            return
        
        # Clear canvas
        ctx.clearRect(0, 0, width, height)
        
        # Get pendulum positions
        x1, y1, x2, y2 = pendulum.get_positions()
        
        # Scale and translate positions to canvas coordinates
        px1 = center_x + x1 * scale
        py1 = center_y + y1 * scale
        px2 = center_x + x2 * scale
        py2 = center_y + y2 * scale
        
        # Draw trail if enabled
        if show_trail:
            tip_history = pendulum.get_tip_history()
            if len(tip_history) > 1:
                ctx.beginPath()
                
                # Start from the oldest point
                first_point = tip_history[0]
                ctx.moveTo(center_x + first_point[0] * scale, center_y + first_point[1] * scale)
                
                # Draw lines to each subsequent point
                for i in range(1, len(tip_history)):
                    x, y = tip_history[i]
                    ctx.lineTo(center_x + x * scale, center_y + y * scale)
                
                # Set trail style
                ctx.strokeStyle = "#FF5733"  # Bright orange
                ctx.lineWidth = 2
                ctx.stroke()
        
        # Draw pendulum rods
        ctx.beginPath()
        ctx.moveTo(center_x, center_y)
        ctx.lineTo(px1, py1)
        ctx.lineTo(px2, py2)
        ctx.strokeStyle = "#2C3E50"  # Dark blue
        ctx.lineWidth = 3
        ctx.stroke()
        
        # Draw pendulum bobs
        # First bob
        ctx.beginPath()
        ctx.arc(px1, py1, 10, 0, 2 * np.pi)
        ctx.fillStyle = "#3498DB"  # Blue
        ctx.fill()
        
        # Second bob
        ctx.beginPath()
        ctx.arc(px2, py2, 10, 0, 2 * np.pi)
        ctx.fillStyle = "#E74C3C"  # Red
        ctx.fill()
        
        # Draw pivot point
        ctx.beginPath()
        ctx.arc(center_x, center_y, 5, 0, 2 * np.pi)
        ctx.fillStyle = "#2C3E50"  # Dark blue
        ctx.fill()
    except Exception as e:
        log_message(f"ERROR drawing: {str(e)}")

def animation_loop(timestamp):
    """Main animation loop."""
    global animation_id, running
    
    try:
        if pendulum is None or not running:
            return
        
        # Check if simulation time has exceeded max time
        if pendulum.get_time() >= max_time:
            running = False
            play_button = js.document.getElementById("play-button")
            play_button.textContent = "Play/Pause"
            return
        
        # Update simulation state
        pendulum.step()
        
        # Update UI
        update_time_display()
        
        # Draw the pendulum
        draw()
        
        # Schedule next frame
        animation_id = js.window.requestAnimationFrame(create_proxy(animation_loop))
    except Exception as e:
        log_message(f"ERROR in animation loop: {str(e)}")
        running = False

def init():
    """Initialize the application."""
    global initialized
    
    # Check if already initialized to avoid double initialization
    if initialized:
        log_message("Already initialized, skipping")
        return
    
    try:
        log_message("Initializing application...")
        
        # Set up canvas
        if not setup_canvas():
            log_message("Failed to set up canvas")
            js.document.getElementById("debug-output").innerHTML += '<p class="error">Failed to set up canvas. Check console for errors.</p>'
            return
        
        # Update the debug panel
        debug_div = js.document.getElementById("debug-output")
        if debug_div:
            debug_div.innerHTML += '<p style="color: green;">Canvas initialized successfully! Red test rectangle should be visible.</p>'
        
        # Attach event handlers
        log_message("Attaching event handlers...")
        
        try:
            # Get UI elements
            play_button = js.document.getElementById("play-button")
            restart_button = js.document.getElementById("restart-button")
            trail_checkbox = js.document.getElementById("show-trail")
            full_trail_checkbox = js.document.getElementById("keep-full-trail")
            
            if play_button is None:
                log_message("ERROR: Play button not found!")
                js.document.getElementById("debug-output").innerHTML += '<p class="error">Play button not found. Check HTML structure.</p>'
                return
                
            if restart_button is None:
                log_message("ERROR: Restart button not found!")
                js.document.getElementById("debug-output").innerHTML += '<p class="error">Restart button not found. Check HTML structure.</p>'
                return
                
            if trail_checkbox is None:
                log_message("ERROR: Trail checkbox not found!")
                js.document.getElementById("debug-output").innerHTML += '<p class="error">Trail checkbox not found. Check HTML structure.</p>'
                return
            
            # Create proxied event handlers
            toggle_proxy = create_proxy(toggle_simulation)
            restart_proxy = create_proxy(restart_simulation)
            trail_proxy = create_proxy(toggle_trail)
            full_trail_proxy = create_proxy(toggle_full_trail)
            
            # Add event listeners
            play_button.addEventListener("click", toggle_proxy)
            restart_button.addEventListener("click", restart_proxy)
            trail_checkbox.addEventListener("change", trail_proxy)
            if full_trail_checkbox:
                full_trail_checkbox.addEventListener("change", full_trail_proxy)
            
            # Add event listeners for input fields
            theta1_input = js.document.getElementById("theta1")
            theta2_input = js.document.getElementById("theta2")
            sim_length_input = js.document.getElementById("simulation-length")
            
            if theta1_input and theta2_input and sim_length_input:
                # Create a function to notify user to restart
                def notify_restart(event=None):
                    js.document.getElementById("restart-notice").style.display = "block"
                    js.setTimeout(lambda: js.document.getElementById("restart-notice").classList.add("flash"), 100)
                
                # Add event listeners
                theta1_input.addEventListener("change", create_proxy(notify_restart))
                theta2_input.addEventListener("change", create_proxy(notify_restart))
                sim_length_input.addEventListener("change", create_proxy(notify_restart))
                
                # Also make input fields trigger restart on Enter key
                def handle_enter_key(event):
                    if event.key == "Enter":
                        restart_simulation()
                
                theta1_input.addEventListener("keyup", create_proxy(handle_enter_key))
                theta2_input.addEventListener("keyup", create_proxy(handle_enter_key))
                sim_length_input.addEventListener("keyup", create_proxy(handle_enter_key))
            else:
                log_message("WARNING: Could not find all input elements")
            
            log_message("Event handlers attached successfully")
            
            # Also create direct event handler bindings for debugging
            js.window.toggleSimulation = toggle_proxy
            js.window.restartSimulation = restart_proxy
            js.window.toggleTrail = trail_proxy
            js.window.toggleFullTrail = full_trail_proxy
            
            # Add debug buttons to debug panel
            debug_buttons_html = '<div class="debug-buttons">' + \
                '<button onclick="window.toggleSimulation()" class="button primary">Debug: Toggle Simulation</button> ' + \
                '<button onclick="window.restartSimulation()" class="button secondary">Debug: Restart</button>' + \
                '<button onclick="window.toggleTrail()" class="button secondary">Debug: Toggle Trail</button>' + \
                '<button onclick="window.toggleFullTrail()" class="button secondary">Debug: Toggle Full Trail</button>' + \
                '</div>'
            debug_div.innerHTML += debug_buttons_html
            
        except Exception as e:
            log_message(f"ERROR attaching event handlers: {str(e)}")
            js.document.getElementById("debug-output").innerHTML += f'<p class="error">Error attaching event handlers: {str(e)}</p>'
            return
        
        # Initialize simulation
        log_message("Setting up initial simulation...")
        init_simulation()
        
        # Update PyScript status
        js.document.getElementById("pyscript-status").textContent = "Loaded and Ready"
        js.document.getElementById("pyscript-status").style.color = "green"
        
        # Auto-start the simulation to demonstrate it works
        js.setTimeout(create_proxy(lambda: toggle_simulation()), 1000)
        
        # Mark as initialized
        initialized = True
        
        log_message("Initialization complete!")
    except Exception as e:
        log_message(f"ERROR during initialization: {str(e)}")
        js.document.getElementById("debug-output").innerHTML += f'<p class="error">Error during initialization: {str(e)}</p>'

# Run initialization when the script loads
log_message("Script loaded, running manual initialization...")

# Use try/except for safety
try:
    # Initialize after a short delay to ensure DOM is ready
    js.setTimeout(create_proxy(init), 500)
    
    # Also register a load event handler as backup
    js.window.addEventListener("load", create_proxy(init))
    
    # Create a global manual init function
    js.window.manualInit = create_proxy(init)
    
    # Add a manual init button after a delay
    def add_manual_button():
        try:
            debug_div = js.document.getElementById("debug-output")
            if debug_div:
                debug_div.innerHTML += '<p><button onclick="window.manualInit()" class="button primary">Manual Init</button></p>'
        except Exception as e:
            log_message(f"Error adding manual button: {str(e)}")
    
    js.setTimeout(create_proxy(add_manual_button), 1000)
    
except Exception as e:
    log_message(f"ERROR during script initialization: {str(e)}")
    try:
        js.document.getElementById("debug-output").innerHTML += f'<p class="error">Script initialization error: {str(e)}</p>'
    except:
        pass 