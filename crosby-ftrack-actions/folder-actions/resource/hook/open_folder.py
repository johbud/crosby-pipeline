
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
    
    
class OpenFolder(BaseAction):

    
    label = 'Open folder'
    identifier = 'open.folder'
    description = 'Open a task or project folder.'
    icon = os.path.join(os.path.dirname(__file__), '..', "icons", "folder_find.png")


    def launch(self, session, entities, event) -> dict:

        entity_type, entity_id = entities[0]

        #location = self.session.pick_location()
        #self.logger.info('Using location {}'.format(location['name']))


        path: str = ""

        folder_helper = FolderHelper(session, self.logger)
        prefix = folder_helper.get_prefix(None)

        if entity_type == "Project":
            project = self.session.query(f'Project where id is { entity_id }').first()
            path = os.path.join(prefix, project['name'])

        elif entity_type == "TypedContext":
            task = self.session.query(f'Task where id is {entity_id}').first()
            
            parents = folder_helper.get_parents(task)
            parents_path = ""
            for p in parents:
                parents_path = os.path.join(parents_path, folder_helper.fix_name(p['name']))

            path = os.path.join(prefix, task['project']['name'], "02_work", parents_path, folder_helper.fix_name(task['name']))
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

    action: OpenFolder = OpenFolder(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(server_url=FTRACK_SERVER, api_user=FTRACK_API_USER, api_key=FTRACK_API_KEY, auto_connect_event_hub=True)
    register(session)

    session.event_hub.wait()

