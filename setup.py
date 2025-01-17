"""
The setup.py files is an essential part of packaging and
distributing Python Projects. It is used by setuptools
(or distutils in older python version) to define the configuration
of your project, such as it metadata, dependencies and more
"""

from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:
    """
    This function will return list of requirements
    """

    requirement_lst:list[str]=[]
    try:
        with open("requirements.txt", "r") as file:
            # Read lines form the files
            lines=file.readlines()
            ## Process each line
            for line in lines:
                requirement=line.strip()
                ## ignore empty line and -e .
                if requirement and requirement!="-e .":
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not exists.")

    
    return requirement_lst

setup(
    name = "NetworkSecurity",
    version="0.0.1",
    author="Ankit Mishra",
    author_email="abc@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)