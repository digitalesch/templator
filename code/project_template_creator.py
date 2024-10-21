# std-lib imports
from dataclasses import dataclass
import os
import yaml
import re
from shutil import copyfile
import argparse
import shutil

# 3rd party imports
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import CookiecutterException

@dataclass
class ProjectTemplateCreator():
    template_name: str
    root_dir: str
    extensions: list

    def check_if_folder_exists(
        self,
        path: str
    ) -> None:
        try:
            os.makedirs(path)
        except FileExistsError:
            print(f'Folder {path} already exist!')

    def create_template_paths(
        self
    ) -> None:
        self.paths = {
            'root':             self.root_dir,
            'definitions':      os.path.join(self.root_dir,'definitions'),
            'templates':        os.path.join(self.root_dir,'templates',self.template_name),
            'skeleton':         os.path.join(self.root_dir,'templates',self.template_name,'skeleton'),
            'generated':        os.path.join(self.root_dir,'templates',self.template_name,'generated'),
        }
        self.check_if_folder_exists(self.paths['generated'])
        self.check_if_folder_exists(self.paths['skeleton'])

    # # reads the stream path to get yaml dict with help of Loader: YamlLoader
    def read_file_structure_file(
        self,
        file_path: str
    ) -> None:
        with open(f"{self.root_dir}/{file_path}",'r') as yaml_file:
            self.file_structure = yaml.safe_load(yaml_file)

    def materialize_file_structure(
        self,
        foldeir_structure: dict,
        output_path: str
    ) -> None:
        if isinstance(foldeir_structure,dict):
            for key,value in foldeir_structure.items():
                if not any([re.findall('\.'+extension+'$',key) for extension in self.extensions]):
                    self.check_if_folder_exists(os.path.join(output_path,key))
                    self.materialize_file_structure(value,os.path.join(output_path,key))
                else:
                    copyfile(
                        os.path.join(self.paths['templates'],value),
                        os.path.join(output_path,key)
                    )
        else:
            # list
            try:
                if isinstance(foldeir_structure,list):
                    for item in foldeir_structure:
                        for key,value in item.items():
                            copyfile(
                                os.path.join(self.paths['templates'],value),
                                os.path.join(output_path,key)
                            )
            # when metadata is defined, the origin doesn't have the same file
            except:
                pass

    def materialize_template(
        self
    ) -> None:
        # creates templated folders / files
        try:
            cookiecutter(
                template=self.paths['skeleton'],
                no_input=True,
                output_dir=self.paths['generated'],
                overwrite_if_exists=True
            )
            print("Project templated successfully!")
        except CookiecutterException as e:
            print(f"Error occurred while creating project: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser()
    
    arguments_list = [
        {'name':'--template_name','type':str,'help':'specify template name to construct folders/files'},
        # {'name':'--remake','default':False,'type':bool,'help':'specifies if you want to remake generated file structure'}
    ]
    
    for arg in arguments_list:
        parser.add_argument(
            arg['name'],
            default=arg['default'] if 'default' in arg else None,
            type=arg['type'],
            help=arg['help'],
            required=True,
        )

    arguments = parser.parse_args()
    
    project_template = ProjectTemplateCreator(
        template_name=arguments.template_name,
        root_dir='.',
        extensions=['yaml','yml','py','json']
    )

    project_template.read_file_structure_file(
        f'templates/{arguments.template_name}/definitions/template_directory.yaml'
    )

    project_template.create_template_paths()
    project_template.materialize_file_structure(
        project_template.file_structure,
        project_template.paths['skeleton']
    )
    project_template.materialize_template()

if __name__ == "__main__":
    main()