import os
import logging
import ftrack_api
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

    
class RenameTask(BaseAction):

    label = 'Rename task'
    identifier = 'rename.task'
    description = 'Rename the selected task.'

    def interface(self, session, entities, event):

        logging.info("Launched.")

        values = event['data'].get('values', {})
        if values:
            return

        entity_type, entity_id = entities[0]
        task = session.get(entity_type, entity_id)

        widgets = [
            {
                'label': 'New name: ',
                'type': 'text',
                'name': 'new_name',
                'value': task['name']
            },
            {
                'label': 'Rename folder on server: ',
                'type': 'boolean',
                'name': 'rename_folder',
                'value': True
            }
        ]

        return widgets


    def launch(self, session, entities, event) -> dict:

        logging.info("Launched.")

        entity_type, entity_id = entities[0]
        task = session.get(entity_type, entity_id)
        original_name = task['name']

        values = event['data'].get('values', {})

        if values:
            for key, value in values.items():
                print(key)
                print(value)
                print(task)

            try:
                session.get('Task', entity_id)['name'] = values['new_name']
                session.commit()
            except:
                return {
                "success": False, 
                "message": f"Failed to rename task."
                }
            
            if values['rename_folder']:
                folder_helper = FolderHelper(session, self.logger)
                new_path = folder_helper.make_task_path(task)
                original_path = os.path.join(os.path.split(new_path)[0], folder_helper.fix_name(original_name))
                
                print(original_path)
                print(new_path)

                rename_result = folder_helper.rename_folder(original_path, new_path)

                if isinstance(rename_result, Exception):
                    return {
                        "success": False, 
                        "message": f"Failed to rename folder: {str(rename_result)}"
                        }

        return {
                "success": True, 
                "message": f"Renamed task: {task['name']}"
                }


    def discover(self, session, entities, event):
        
        if not entities:
            return False
        
        entity_type, entity_id = entities[0]
        
        logging.info("Discovered, with entity_type: " + entity_type)

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

    def register(self) -> None:

        '''Register action.'''
        self.session.event_hub.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                self.session.api_user
            ),
            self._discover
        )
        logging.info("Registered discover-function.")

        self.session.event_hub.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0} and '
            'source.user.username={1}'.format(
                self.identifier,
                self.session.api_user
            ),
            self._launch
        )
        logging.info("Registered launch-function.")


def register(session, **kw) -> None:
    
    if not isinstance(session, ftrack_api.Session):
        return

    action: RenameTask = RenameTask(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(auto_connect_event_hub=True)
    register(session)

    logging.info("Waiting...")
    session.event_hub.wait()

