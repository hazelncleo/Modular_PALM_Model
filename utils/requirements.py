
class Requirements:
    def __init__(
        self,
        software: list[str],
        analysis: list[str],
        geometry: list[str],
        material: list[str]
    ) -> None:
        
        self.software = software
        self.analysis = analysis
        self.geometry = geometry
        self.material = material
    
    @classmethod
    def from_dict(cls, data_dict: dict) -> Requirements:       
        ''''''
        return cls(
            software = data_dict['software'],
            analysis = data_dict['analysis'],
            geometry = data_dict['geometry'],
            material = data_dict['material']
        )
        
    @classmethod
    def load_from_file(cls, requirements_file_name: str) -> Requirements:
        ''''''
        try:
            with open(requirements_file_name, 'r') as requirements_file:
                data_dict = json.load(requirements_file)
        except:
            FileNotFoundError(f'Error reading the file: "{requirements_file_name}".')
                   
        return cls(
            software = data_dict['software'],
            analysis = data_dict['analysis'],
            geometry = data_dict['geometry'],
            material = data_dict['material']
        )
    
    def add_requirements_from_dict(self, data_dict: dict) -> None:
        ''''''
        self.software.extend([requirement for requirement in data_dict['software'] if requirement not in self.software])
        self.analysis.extend([requirement for requirement in data_dict['analysis'] if requirement not in self.analysis])
        self.geometry.extend([requirement for requirement in data_dict['geometry'] if requirement not in self.geometry])
        self.material.extend([requirement for requirement in data_dict['material'] if requirement not in self.material])