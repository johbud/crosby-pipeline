import ftrack_api
import logging
import json
import os
import sys

from ftrack_api import Session
from ftrack_action_handler.action import BaseAction

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
    

class MakeTaskFolder(BaseAction):

    
    label = 'Create a task folder'
    identifier = 'create.folder.task'
    description = 'Create a folder for the selected task.'


    def launch(self, session, entities, event) -> dict:

        entity_type, entity_id = entities[0]

        task = self.session.query(f'Task where id is {entity_id}').one()

        folder_helper = FolderHelper(session, self.logger)

        if not os.path.exists(folder_helper.config_file):
            return {
                "success": False, 
                "message": f"Could not find template. {folder_helper.config_file}"
                }

        make_folders_result = folder_helper.make_task_folder(task['project'], task)

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
        
        
    def register(self):
        '''Register action.'''
        self.session.event_hub.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                self.session.api_user
            ),
            self._discover
        )

        self.session.event_hub.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0} and '
            'source.user.username={1}'.format(
                self.identifier,
                self.session.api_user
            ),
            self._launch
        )



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

