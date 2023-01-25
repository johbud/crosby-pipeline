
import os
import sys
import logging

dependencies_directory = os.path.abspath(
  os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

import ftrack_api
from ftrack_api import Session
from ftrack_action_handler.action import BaseAction
from showinfm import show_in_file_manager

FTRACK_SERVER = "https://crosby.ftrackapp.com"
FTRACK_API_KEY = "MjFlNThhNzgtYmI1Yy00NTYzLWJiODctYmFjNmViNDkwMzE1OjowZTNkMGJhMi1kZDI1LTQyNDUtOTZiMC0wOTUwNWU4NjA1ZWU"
FTRACK_API_USER = "john.buddee@crosby.se"

class OpenFolder(BaseAction):

    
    label = 'Open folder'
    identifier = 'open.folder'
    description = 'Open a task or project folder.'
    icon = os.path.join(os.path.dirname(__file__), '..', "icons", "folder_find.png")

    def get_parent(self, entity):
        parent = self.session.query(f'select id from TypedContext where id is { entity["parent_id"]}').first()

        return parent
    

    def get_parents(self, entity):
        parents = []
        
        next = entity

        while next:
            parent = self.get_parent(next)
            if parent:
                parents.append(parent)
            next = parent

        parents.reverse()
        return parents


    def fix_name(self, name: str)->str:
        
        fixed_name = ""

        for s in name:
            if s == " " or s == "-":
                s = "_"
            if s.isalnum() or s == "_":
                fixed_name += s

        fixed_name = fixed_name.lower()

        return fixed_name


    def launch(self, session, entities, event) -> dict:

        entity_type, entity_id = entities[0]

        location = self.session.pick_location()
        self.logger.info('Using location {}'.format(location['name']))

        prefix = location.accessor.prefix

        path: str = ""

        if entity_type == "Project":
            project = self.session.query(f'Project where id is { entity_id }').first()
            path = os.path.join(prefix, project['name'])

        elif entity_type == "TypedContext":
            task = self.session.query(f'Task where id is {entity_id}').first()
            
            parents = self.get_parents(task)
            parents_path = ""
            for p in parents:
                parents_path = os.path.join(parents_path, self.fix_name(p['name']))

            path = os.path.join(prefix, task['project']['name'], "02_work", parents_path, self.fix_name(task['name']))
            self.logger.info("Opening path: " + path)

        if not os.path.exists(path):
            message = "Folder does not exist."
            self.logger.warning(message)
            return {
                "success": False, 
                "message": message
                }

        try:
            show_in_file_manager(path)
        except Exception as err:
            self.logger.error(str(err))
            return {
                "success": False, 
                "message": str(err)
                }
        
        return {
                "success": True, 
                "message": f"Opened: {path}"
                }
    

    def discover(self, session, entities, event):

        if not entities:
            return False
        
        entity_type, entity_id = entities[0]

        if not (entity_type == "TypedContext" or entity_type == "Project"):
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

        elif entity_type == "Project":
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

    action: OpenFolder = OpenFolder(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(server_url=FTRACK_SERVER, api_user=FTRACK_API_USER, api_key=FTRACK_API_KEY, auto_connect_event_hub=True)
    register(session)

    session.event_hub.wait()

