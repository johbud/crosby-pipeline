import ftrack_api
import logging
import json
import os
from ftrack_api import Session
from ftrack_action_handler.action import BaseAction

FTRACK_SERVER = "https://crosby.ftrackapp.com"
FTRACK_API_KEY = "MjFlNThhNzgtYmI1Yy00NTYzLWJiODctYmFjNmViNDkwMzE1OjowZTNkMGJhMi1kZDI1LTQyNDUtOTZiMC0wOTUwNWU4NjA1ZWU"
FTRACK_API_USER = "john.buddee@crosby.se"

class MakeTaskFolder(BaseAction):

    
    label = 'Create a task folder'
    identifier = 'create.folder.task'
    description = 'Create a folder for the selected task.'

    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "templates", "folders.json")


    def iterate_and_create_folder(self, folders, _parent):
        for folder, children in folders.items():
            path = os.path.join(_parent, folder)

            make_folder = self.make_folder(path)

            if isinstance(make_folder, Exception):
                return make_folder
            
            self.logger.info("Created: " + path)

            if children:
                make_children = self.iterate_and_create_folder(children, os.path.join(_parent, folder))
                if isinstance(make_children, Exception):
                    return make_folder
        return True


    def fix_name(self, name: str)->str:
        
        fixed_name = ""

        for s in name:
            if s == " " or s == "-":
                s = "_"
            if s.isalnum() or s == "_":
                fixed_name += s

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

            path = os.path.join(prefix, project['name'], "02_work", parents_path , task['name'])
            
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
            os.makedirs(path)
        except Exception as err:
            return err
        
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


    def launch(self, session, entities, event) -> dict:

        entity_type, entity_id = entities[0]

        task = self.session.query(f'Task where id is {entity_id}').one()

        if not os.path.exists(self.config_file):
            return {
                "success": False, 
                "message": f"Could not find template. {self.config_file}"
                }

        make_folders_result = self.make_task_folder(task['project'], task)

        if isinstance(make_folders_result, Exception):
            return {
                "success": False, 
                "message": f"Could not create folder: " + str(make_folders_result)
                }
        else:
            return {
                "success": True, 
                "message": f"Created folder for task: { task['name'] }"
                }
            

    def discover(self, session, entities, event):

        if not entities:
            return False
        
        entity_type, entity_id = entities[0]

        if entity_type != "TypedContext":
            return False

        entity = session.get(entity_type, entity_id)

        if entity['context_type'] == "task":
            return {
            'items': [{
                'label': self.label,
                'description': self.description,
                'actionIdentifier': self.identifier
            }]
        }

        else:
            return False  


def register(session, **kw) -> None:
    
    if not isinstance(session, ftrack_api.Session):
        return

    action: MakeTaskFolder = MakeTaskFolder(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(server_url=FTRACK_SERVER, api_user=FTRACK_API_USER, api_key=FTRACK_API_KEY, auto_connect_event_hub=True)
    register(session)

    session.event_hub.wait()

