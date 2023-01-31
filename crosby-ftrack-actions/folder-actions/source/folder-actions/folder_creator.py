import os
import sys
import json

class FolderCreator():

    def iterate_and_create_folder(self, folders, _parent):
        for folder, children in folders.items():
            path = os.path.join(_parent, folder)

            make_folder = self.make_folder(path)

            if isinstance(make_folder, Exception):
                return make_folder
            
            print("Created: " + path)

            if children:
                make_children = self.iterate_and_create_folder(children, os.path.join(_parent, folder))
                if isinstance(make_children, Exception):
                    return make_folder
        return True
    
    
    def make_project_folder(self, project):
        
        location = self.session.pick_location()
        self.logger.info('Using location {}'.format(location['name']))

        prefix = location.accessor.prefix

        with open(self.config_file) as f:
            j = json.load(f)

            parent = os.path.join(prefix, project['name'])
            make_folder = self.make_folder(parent)

            if isinstance(make_folder, Exception):
                return make_folder

            print("Created: " + parent)
            self.iterate_and_create_folder(j['folders'], parent)

        return True
    

    def fix_name(self, name: str)->str:
        
        fixed_name = ""

        for s in name:
            if s == " " or s == "-":
                s = "_"
            if s.isalnum() or s == "_":
                fixed_name += s

        fixed_name = fixed_name.lower()

        return fixed_name


    def make_task_folder(self, project, task):

        location = self.session.pick_location()

        prefix = location.accessor.prefix

        parents = self.get_parents(task)
        parents_path = ""
        for p in parents:
            parents_path = os.path.join(parents_path, self.fix_name(p['name']))
            self.logger.info(f'Parent folders: { parents_path }')


        with open(self.config_file) as f:
            j = json.load(f)

            self.logger.info('Using location {}'.format(location['name']))
            self.logger.info(f'Work drive: { prefix }')

            path = os.path.join(prefix, project['name'], "02_work", parents_path , self.fix_name(task['name']))
            
            self.logger.info(f'Path: {path}')
            
            if not os.path.exists(os.path.join(prefix, project['name'])):
                self.logger.error("Project folder does not exist.")
                return Exception("Project folder does not exist.")

            make_folder_result = self.iterate_and_create_folder(j['folders'], path)
            
            if isinstance(make_folder_result, Exception):
                    return make_folder_result
        
        return True
    

    def make_folder(self, path):
        try:
            os.mkdir(path)
        except Exception as err:
            return err
        
        return True