import os
import sys
import json
import ftrack_api
import logging

class FolderHelper():

    def __init__(self, session, logger):
        self.session = session
        self.logger = logger

    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config", "folders.json")

    def get_prefix(self, config):

        if config is None:
            with open(self.config_file) as f:
                config = json.load(f)
                
        if sys.platform == "darwin":
            return config['drive_macos']
        
        if sys.platform == "win32":
            return config['drive_win']
           

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
        
        #location = self.session.pick_location()
        #self.logger.info('Using location {}'.format(location['name']))
        #prefix = location.accessor.prefix

        with open(self.config_file) as f:
            j = json.load(f)

            prefix = self.get_prefix(j)
            self.logger.info("Prefix: " + prefix)
            parent = os.path.join(prefix, project['name'])
            make_folder = self.make_folder(parent)

            if isinstance(make_folder, Exception):
                return make_folder

            print("Created: " + parent)
            self.iterate_and_create_folder(j['project_folders'], parent)

        return True
    

    def fix_name(self, name: str)->str:
        fixed_name = ""

        for s in name:
            if s == "å" or s == "Å":
                s = "a"
            if s == "ä" or s == "Ä":
                s = "a"
            if s == "ö" or s == "Ö":
                s = "o"
            if s == " " or s == "-":
                s = "_"
            if s.isalnum() or s == "_":
                fixed_name += s

        fixed_name = fixed_name.lower()

        return fixed_name


    def make_task_folder(self, project, task):

        #location = self.session.pick_location()
        #prefix = location.accessor.prefix

        parents = self.get_parents(task)
        parents_path = ""
        for p in parents:
            parents_path = os.path.join(parents_path, self.fix_name(p['name']))
            self.logger.info(f'Parent folders: { parents_path }')


        with open(self.config_file) as f:
            j = json.load(f)

            prefix = self.get_prefix(j)
            
            #self.logger.info('Using location {}'.format(location['name']))
            self.logger.info(f'Work drive: { prefix }')

            path = os.path.join(prefix, project['name'], "02_work", parents_path , self.fix_name(task['name']))
            
            self.logger.info(f'Path: {path}')
            
            if not os.path.exists(os.path.join(prefix, project['name'])):
                self.logger.error("Project folder does not exist.")
                return Exception("Project folder does not exist.")

            make_folder_result = self.iterate_and_create_folder(j['task_folders'], path)
            
            if isinstance(make_folder_result, Exception):
                    return make_folder_result
        
        return True
    

    def get_parent(self, entity):
        parent = self.session.query(f'select id from TypedContext where id is { entity["parent_id"]}').first()

        return parent
    

    def get_parents(self, entity):
        parents = []
        
        next = entity

        while next:
            parent = self.get_parent(next)
            if parent:
                print(parent['name'])
                parents.append(parent)
            next = parent

        parents.reverse()
        return parents


    def make_folder(self, path):
        try:
            os.makedirs(path)
        except Exception as err:
            return err
        
        return True