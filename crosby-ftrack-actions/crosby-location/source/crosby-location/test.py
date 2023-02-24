import ftrack_api
import logging
import json
import os
import sys

from ftrack_api import Session
from ftrack_action_handler.action import BaseAction

FTRACK_SERVER = "https://crosby.ftrackapp.com"
FTRACK_API_KEY = "MjFlNThhNzgtYmI1Yy00NTYzLWJiODctYmFjNmViNDkwMzE1OjowZTNkMGJhMi1kZDI1LTQyNDUtOTZiMC0wOTUwNWU4NjA1ZWU"
FTRACK_API_USER = "john.buddee@crosby.se"

class TestLocation(BaseAction):

    label = 'Test location'
    identifier = 'test.location'
    description = 'Test location'


    def launch(self, session, entities, event) -> dict:

        location = session.pick_location()

        return {
            "success": True, 
            "message": f"Test! Location: { location['name'] }"
            }
        

    def discover(self, session, entities, event):

        return {
            'items': [{
                'label': self.label,
                'description': self.description,
                'actionIdentifier': self.identifier
            }]
        }


def register(session, **kw) -> None:
    
    if not isinstance(session, ftrack_api.Session):
        return

    action = TestLocation(session)
    action.register()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session: Session = ftrack_api.Session(server_url=FTRACK_SERVER, api_user=FTRACK_API_USER, api_key=FTRACK_API_KEY, auto_connect_event_hub=True)
    register(session)

    session.event_hub.wait()

