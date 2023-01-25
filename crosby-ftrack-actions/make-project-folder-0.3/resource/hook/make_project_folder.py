import ftrack_api
import logging
import json
import os
from ftrack_api import Session
from ftrack_action_handler.action import BaseAction

FTRACK_SERVER = "https://crosby.ftrackapp.com"
FTRACK_API_KEY = "MjFlNThhNzgtYmI1Yy00NTYzLWJiODctYmFjNmViNDkwMzE1OjowZTNkMGJhMi1kZDI1LTQyNDUtOTZiMC0wOTUwNWU4NjA1ZWU"
FTRACK_API_USER = "john.buddee@crosby.se"

class MakeProjectFolder(BaseAction):

    
    label = 'Create a project folder'
    identifier = 'create.folder.project'
    description = 'Create a folder for the selected project.'

    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "templates", "folders.json")


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


    def make_folder(self, path):
        try:
            os.mkdir(path)
        except Exception as err:
            return err
        
        return True


    def launch(self, session, entities, event) -> dict:

        entity_type, entity_id = entities[0]

        project = self.session.query(f'Project where id is {entity_id}').first()

        if not os.path.exists(self.config_file):
            return {
                "success": False, 
                "message": f"Could not find template. {self.config_file}"
                }

        make_folders = self.make_project_folder(project)

        if isinstance(make_folders, Exception):
            return {
                "success": False, 
                "message": f"Could not create folder: " + str(make_folders)
                }
        else:
            return {
                "success": True, 
                "message": f"Created folder for project: { project['name'] }"
                }
            

    def discover(self, session, entities, event):

        if not entities:
            return False

        entity_type, entity_id = entities[0]

        if entity_type == "Project":
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

    action: MakeProjectFolder = MakeProjectFolder(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(server_url=FTRACK_SERVER, api_user=FTRACK_API_USER, api_key=FTRACK_API_KEY, auto_connect_event_hub=True)
    register(session)

    session.event_hub.wait()

