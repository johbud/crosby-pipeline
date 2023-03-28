import os
import logging
import ftrack_api
from ftrack_api import Session
from ftrack_action_handler.action import BaseAction

    
class ChangeParentTask(BaseAction):

    label = 'Change parent task'
    identifier = 'change.parent.task'
    description = 'Change the parent task of selected version.'

    def interface(self, session, entities, event):

        logging.info("Launched.")

        values = event['data'].get('values', {})
        if values:
            return

        entity_type, entity_id = entities[0]
        version = session.get(entity_type, entity_id)

        task = list()
        for link in version['link']:
            if link['type'] == "Project":
                logging.info('Project is: ' + str(link['name']))
                tasks = session.query(f'Task where project.name is {link["name"]}').all()
                break
        print("Found tasks: ")
        
        task_select = list()

        for task in tasks:
            print(task['name'])
            task_select.append({'label': str(task['parent']['name']) + " / " + str(task['name']), 'value': task['id'] })


        widgets = [
            {
                'label': 'Set parent task for version',
                'type': 'enumerator',
                'name': version['id'],
                'data': task_select
            }
        ]

        return widgets

    def launch(self, session, entities, event) -> dict:

        logging.info("Launched.")

        entity_type, entity_id = entities[0]
        version = session.get(entity_type, entity_id)

        task = list()
        for link in version['link']:
            if link['type'] == "Project":
                project_name = link['name']
                logging.info('Project is: ' + str(link['name']))
                tasks = session.query(f'Task where project.name is {link["name"]}').all()
                break

        print("Found tasks: ")
        for task in tasks:
            print(task['name'])

        values = event['data'].get('values', {})

        task_id = str()
        task_name = str()

        if values:
            for key, value in values.items():
                task_id = value

            print(task_name)

        task = session.query(f"Task where id is {task_id}").one()

        session.get('AssetVersion', entity_id)['task'] = task
        session.get('AssetVersion', entity_id)['task_id'] = task_id

        session.commit()

        return {
                "success": True, 
                "message": f"Changed parent task to: {task['name']}"
                }


    def discover(self, session, entities, event):
        
        if not entities:
            return False
        
        entity_type, entity_id = entities[0]
        
        logging.info("Discovered, with entity_type: " + entity_type)

        if not (entity_type == "AssetVersion"):
            return False

        return {
            'items': [{
                'label': self.label,
                'description': self.description,
                'actionIdentifier': self.identifier
            }]
        }


    def register(self):

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

    action: ChangeParentTask = ChangeParentTask(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(auto_connect_event_hub=True)
    register(session)

    logging.info("Waiting...")
    session.event_hub.wait()

