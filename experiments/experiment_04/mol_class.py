from dataclasses import dataclass
import numpy as np

R = 0.08314462  # ideal gas constant [bar·L/mol·K]

@dataclass
class MoleculeClass:
    A: float
    B: float
    C: float
    
    Tc: float = None
    Pc: float = None
    w: float = None
    k: float = 0.0
    
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
    
    def gamma(self, x: float, A: float) -> float:
        # calculate activity coefficient using Wilson model
        # A is the interaction parameter
        gamma = np.exp(A * ((1 - x) ** 2))
        return gamma
    
    def calculate_kappa(self, Tr: float) -> float:
        # calculate kappa for PR EOS alpha function
        if self.w <= 0.49:
            kappa = 0.37464 + 1.54226 * self.w - 0.26992 * self.w ** 2
        else: # Soave type kappa
            kappa = 0.3796 + 1.485 * self.w - 0.1644 * self.w ** 2 + 0.01667 * self.w ** 3
        return kappa
    
    def calculate_alpha(self, Tr: float) -> float:
        kappa = self.calculate_kappa(Tr)
        alpha = (1+kappa * (1-np.sqrt(Tr)))**2
        return alpha
    
    def calculate_a(self, psi: float, T: float)-> float:
        # Calculate PR EOS 'a' parameter
        Tr = T / self.Tc
        alpha = self.calculate_alpha(Tr)
        a = psi * alpha *  (R * self.Tc) ** 2 / self.Pc
        return a
    
    def calculate_b(self, omega: float) -> float:
        # calculate PR EOS 'b' parameter
        b = omega * R * self.Tc / self.Pc
        return b