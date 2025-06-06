from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union

Vector = List[float]
LawFn  = Callable[["SimObject", "System", float], None]



class SimObject:
    def __getitem__(self, key):
        attr, idx = key
        return getattr(self, attr)[idx]

    def __setitem__(self, key, value):
        attr, idx = key
        getattr(self, attr)[idx] = value



#  Particle 

class Particle(SimObject):
    def __init__(
        self,
        mass: float = 1.0,
        position: Optional[Vector] = None,
        velocity: Optional[Vector] = None,
        electric_charge: float = 0.0,
    ) -> None:
        self.mass: float = float(mass)
        self.system: Optional[System] = None
        self.position: Vector = position or [0.0, 0.0, 0.0]
        self.velocity: Vector = velocity or [0.0, 0.0, 0.0]
        self.acceleration: Vector = [0.0, 0.0, 0.0]
        self.electric_charge: float = float(electric_charge)



    def position_at_time(self, t: float) -> List[float]:
        return [self.position[i] + self.velocity[i] * t for i in range(3)]

    def apply_force(self, force: Vector):
        for i in range(3):
            self.acceleration[i] += force[i] / self.mass

    def update(self, dt: float):
        for i in range(3):
            self.velocity[i] += self.acceleration[i] * dt
            self.position[i] += self.velocity[i] * dt
            self.acceleration[i] = 0.0  # resetuj przyspieszenie po każdej klatce




class Field(SimObject):
    def __init__(
        self,
        center: Optional[Vector] = None,
        function: Optional[Callable[["Particle", "Field"], float]] = None,
        radius: float = 1.0,
        intensity: float = 1.0,
    ) -> None:
        self.center: Vector   = center or [0.0, 0.0, 0.0]   # punkt_początkowy
        self.function = function                            # będzie można przypisać square, linear…
        self.radius: float     = float(radius)
        self.intensity: float  = float(intensity)



#  Field (placeholder)

class Field(SimObject):
    def __init__(self) -> None:
        self.radius: float = 1.0
        self.intensity: Union[float, Callable[[float], float]] = 1.0
        self.source_position: Vector = [0.0, 0.0, 0.0]


#  Law wrapper: 
@dataclass
class Law:
    fn: LawFn
    scope: str = "global"     
    target: str = "particle"

    def applies(self, name: str, obj: SimObject) -> bool:
        if self.target == "particle" and not isinstance(obj, Particle):
            return False
        if self.target == "field" and not isinstance(obj, Field):
            return False

        if self.scope == "global":
            return True

        if obj.system is not None and self.scope == obj.system.name:
            return True

        return name == self.scope




#  System
class System:
    def __init__(self, name: str = "root") -> None:
        self.name = name
        self.time: float = 0.0
        self.particles: Dict[str, Particle] = {}
        self.fields:    Dict[str, Field] = {}
        self.laws: List[Law] = []
        self.subsystems: Dict[str, "System"] = {}
        self.parent: Optional["System"] = None

    # --- hierarchy
    def add_subsystem(self, name: str, sys: "System") -> None:
        sys.parent = self
        self.subsystems[name] = sys

    def add_particle(self, name: str, p: Particle):
        self.particles[name] = p
        p.system = self


    def add_field(self, name: str, f: Field):
        self.fields[name] = f

    def register_law(self, law: Law):
        # print(f" Law registered in system '{self.name}': scope={law.scope}")


        self.laws.append(law)

    def step(self, dt: float = 1.0):
        

        active = self._collect_laws()

        for law in active:
            for name, obj in sorted(self.particles.items()):
                if law.applies(name, obj):
                    # print(f"Sprawdzam prawo {law.fn.__name__} dla {name} (system={self.name})")
                    law.fn(obj, self, dt)
            for name, obj in sorted(self.fields.items()):
                if law.applies(name, obj):
                    law.fn(obj, self, dt)

        for p in self.particles.values():
            p.update(dt)

        for sub in self.subsystems.values():
            sub.step(dt)
        

        self.time += dt

    def _collect_laws(self) -> List[Law]:
        if self.parent is None:
            return self.laws.copy()
        return self.parent._collect_laws() + self.laws
