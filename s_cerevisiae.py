from mesa import Agent, Model

class S_Cerevisiae(Agent):
    def __init__(self, unique_id, species_id, model):
        super().__init__(unique_id, model)
        self.species_id = species_id