from dataclasses import dataclass

@dataclass # decorator create variable or attribute for empty classes like self,
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str