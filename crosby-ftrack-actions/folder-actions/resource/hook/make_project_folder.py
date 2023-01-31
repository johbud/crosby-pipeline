import ftrack_api
import logging
import json
import os
import sys

from ftrack_api import Session
from ftrack_action_handler.action import BaseAction

dependencies_directory = os.path.abspath(
  os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

try:
    from ..helpers.folder_helper import FolderHelper
    from ..config.config import FTRACK_API_KEY, FTRACK_API_USER, FTRACK_SERVER
except:
    config_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'config')
        )
    sys.path.append(config_directory)

    helpers_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'helpers')
        )
    sys.path.append(helpers_directory)

    from folder_helper import FolderHelper
    from config import FTRACK_API_KEY, FTRACK_API_USER, FTRACK_SERVER

class MakeProjectFolder(BaseAction):

    label = 'Create a project folder'
    identifier = 'create.folder.project'
    description = 'Create a folder for the selected project.'


    def launch(self, session, entities, event) -> dict:

        entity_type, entity_id = entities[0]

        project = self.session.query(f'Project where id is {entity_id}').first()

        folder_helper = FolderHelper(session, self.logger)

        if not os.path.exists(folder_helper.config_file):
            return {
                "success": False, 
                "message": f"Could not find template. {folder_helper.config_file}"
                }

        make_folders = folder_helper.make_project_folder(project)

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

