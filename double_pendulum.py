import numpy as np
from typing import Tuple, List, Optional

class DoublePendulum:
    """
    Double Pendulum physics simulator.
    
    This class implements the equations of motion for a double pendulum
    and provides methods for numerical integration and state updates.
    """
    
    def __init__(self, 
                 theta1: float = np.pi/2, 
                 theta2: float = np.pi/2,
                 omega1: float = 0.0, 
                 omega2: float = 0.0,
                 length1: float = 1.0, 
                 length2: float = 1.0,
                 mass1: float = 1.0, 
                 mass2: float = 1.0,
                 gravity: float = -9.8,
                 dt: float = 0.01):
        """
        Initialize the double pendulum system.
        
        Args:
            theta1: Initial angle of the first pendulum (in radians)
            theta2: Initial angle of the second pendulum (in radians)
            omega1: Initial angular velocity of the first pendulum
            omega2: Initial angular velocity of the second pendulum
            length1: Length of the first pendulum arm
            length2: Length of the second pendulum arm
            mass1: Mass of the first pendulum bob
            mass2: Mass of the second pendulum bob
            gravity: Gravitational acceleration
            dt: Time step for numerical integration
        """
        # Initial conditions
        self.theta1 = theta1
        self.theta2 = theta2
        self.omega1 = omega1
        self.omega2 = omega2
        
        # Physical parameters
        self.length1 = length1
        self.length2 = length2
        self.mass1 = mass1
        self.mass2 = mass2
        self.gravity = gravity
        
        # Simulation parameters
        self.dt = dt
        self.time = 0.0
        
        # History of the tip position for trail
        self.tip_history: List[Tuple[float, float]] = []
        self.max_history_length = 1000  # Maximum number of positions to store
        
        # Calculate initial positions
        self._update_positions()
    
    def _update_positions(self):
        """Update the positions of the pendulum bobs based on current angles."""
        # Position of the first pendulum bob
        self.x1 = self.length1 * np.sin(self.theta1)
        self.y1 = -self.length1 * np.cos(self.theta1)
        
        # Position of the second pendulum bob
        self.x2 = self.x1 + self.length2 * np.sin(self.theta2)
        self.y2 = self.y1 - self.length2 * np.cos(self.theta2)
        
        # Add current tip position to history
        self.tip_history.append((self.x2, self.y2))
        
        # Limit the history length
        if len(self.tip_history) > self.max_history_length:
            self.tip_history = self.tip_history[-self.max_history_length:]
    
    def _compute_derivatives(self) -> Tuple[float, float, float, float]:
        """
        Compute derivatives for the double pendulum system.
        
        Returns:
            Tuple of (omega1, omega2, alpha1, alpha2) where:
                omega1, omega2 are the angular velocities
                alpha1, alpha2 are the angular accelerations
        """
        # Shorthand variables for readability
        t1, t2 = self.theta1, self.theta2
        w1, w2 = self.omega1, self.omega2
        m1, m2 = self.mass1, self.mass2
        l1, l2 = self.length1, self.length2
        g = self.gravity
        
        # Calculate the derivatives using the equations of motion
        # These are the standard equations for a double pendulum
        
        # Common terms
        delta = t1 - t2
        denom = (2*m1 + m2 - m2 * np.cos(2*delta))
        
        # Angular acceleration for the first pendulum
        num1 = -g*(2*m1 + m2)*np.sin(t1) - m2*g*np.sin(t1 - 2*t2)
        num2 = -2*np.sin(delta)*m2*((w2**2)*l2 + (w1**2)*l1*np.cos(delta))
        alpha1 = (num1 + num2) / (l1 * denom)
        
        # Angular acceleration for the second pendulum
        num1 = 2*np.sin(delta)
        num2 = (w1**2)*l1*(m1 + m2) + g*(m1 + m2)*np.cos(t1) + (w2**2)*l2*m2*np.cos(delta)
        alpha2 = (num1 * num2) / (l2 * denom)
        
        return w1, w2, alpha1, alpha2
    
    def step(self):
        """
        Perform one step of numerical integration using RK4 method.
        Update the system state and increment time.
        """
        # Implement 4th-order Runge-Kutta method
        dt = self.dt
        
        # Initial state
        y = np.array([self.theta1, self.theta2, self.omega1, self.omega2])
        
        # RK4 integration step
        k1 = dt * np.array(self._compute_derivatives_vec(y))
        k2 = dt * np.array(self._compute_derivatives_vec(y + 0.5 * k1))
        k3 = dt * np.array(self._compute_derivatives_vec(y + 0.5 * k2))
        k4 = dt * np.array(self._compute_derivatives_vec(y + k3))
        
        # Update state
        y_new = y + (1/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Update the system state
        self.theta1 = y_new[0]
        self.theta2 = y_new[1]
        self.omega1 = y_new[2]
        self.omega2 = y_new[3]
        
        # Update positions
        self._update_positions()
        
        # Increment time
        self.time += dt
    
    def _compute_derivatives_vec(self, y: np.ndarray) -> Tuple[float, float, float, float]:
        """
        Helper function for RK4 integration that computes derivatives for a state vector.
        
        Args:
            y: State vector [theta1, theta2, omega1, omega2]
            
        Returns:
            Tuple of derivatives [omega1, omega2, alpha1, alpha2]
        """
        # Temporarily store the current state
        theta1_orig, theta2_orig = self.theta1, self.theta2
        omega1_orig, omega2_orig = self.omega1, self.omega2
        
        # Set the state to the input state
        self.theta1, self.theta2 = y[0], y[1]
        self.omega1, self.omega2 = y[2], y[3]
        
        # Compute derivatives
        derivatives = self._compute_derivatives()
        
        # Restore the original state
        self.theta1, self.theta2 = theta1_orig, theta2_orig
        self.omega1, self.omega2 = omega1_orig, omega2_orig
        
        return derivatives
    
    def reset(self, theta1: float = None, theta2: float = None):
        """
        Reset the pendulum to specified initial conditions.
        
        Args:
            theta1: New initial angle for the first pendulum (optional)
            theta2: New initial angle for the second pendulum (optional)
        """
        if theta1 is not None:
            self.theta1 = theta1
        if theta2 is not None:
            self.theta2 = theta2
        
        # Reset velocities and time
        self.omega1 = 0.0
        self.omega2 = 0.0
        self.time = 0.0
        
        # Clear history
        self.tip_history = []
        
        # Update positions
        self._update_positions()
    
    def get_positions(self) -> Tuple[float, float, float, float]:
        """
        Get the current positions of both pendulum bobs.
        
        Returns:
            Tuple of (x1, y1, x2, y2) coordinates
        """
        return self.x1, self.y1, self.x2, self.y2
    
    def get_tip_history(self) -> List[Tuple[float, float]]:
        """
        Get the history of the distal tip positions.
        
        Returns:
            List of (x, y) coordinates
        """
        return self.tip_history

    def get_time(self) -> float:
        """
        Get the current simulation time.
        
        Returns:
            Current time in seconds
        """
        return self.time 

    def set_max_history_length(self, length: Optional[int] = None):
        """
        Set the maximum number of positions to store in the trail history.
        
        Args:
            length: Maximum number of points to keep. If None, keep unlimited history.
        """
        if length is None:
            # Use a very large number to effectively store unlimited history
            self.max_history_length = 1000000
        else:
            self.max_history_length = max(10, length)  # Ensure at least 10 points 