from dataclasses import dataclass
import numpy as np

@dataclass
class MoleculeClass:
    A: float
    B: float
    C: float
    
    Tc: float
    Pc: float
    w: float
    k: float = 0.0
    # will be made in the future when needed
    # def calculate_alpha(self) -> float:
    #     # calculate alpha
    #     alpha = 
    #     return alpha
    def T_sat(self, P: float) -> float:
        # Calculate saturation temperature at given pressure using Antoine equation.
        if P <= 0:
            raise ValueError("Pressure must be positive.")
        t_sat = self.B / (self.A - np.log10(P)) - self.C
        return t_sat
    
    def P_sat(self, T: float) -> float:
        # Antoine equation: log10(P) = A - B/(T + C)
        log_p_sat = self.A - self.B / (T + self.C)
        p_sat = 10 ** log_p_sat
        return p_sat
    
    def gamma(self, x: float, A: float, T: float) -> float:
        # calculate activity coefficient using Wilson model
        # A is the interaction parameter
        gamma = np.exp(A * ((1 - x) ** 2))
        return gamma
    
