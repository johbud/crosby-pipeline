import os
import sys
import functools
import logging
import ftrack_api
import ftrack_api.accessor.disk as _disk
import ftrack_api.structure.standard as _standard

try:
    from . .structures.crosby_structure import CrosbyStructure
except:
    structure_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'structures')
        )
    sys.path.append(structure_directory)
    from crosby_structure import CrosbyStructure
 
logger = logging.getLogger(
   'crosby_location'
)
 
# Name of the location.
LOCATION_NAME = 'testing.jobs02'
 
# Disk mount point.
DISK_PREFIX = 'G:\\'
 
if not os.path.exists(DISK_PREFIX):
   raise Exception('G:-drive not found.')
 
 
def configure_location(session, event):
    '''Listen.'''
    logger.info('Configuring location.')

    location = session.ensure(
        'Location',
        {
            'name': LOCATION_NAME
        }
    )

    location.accessor = _disk.DiskAccessor(
        prefix=DISK_PREFIX
    )
    location.structure = CrosbyStructure()

    # be first to be discovered storage has 95
    location.priority = -100

    logger.warning(
        u'Registering Using location {0} @ {1} with priority {2}'.format(
            LOCATION_NAME, DISK_PREFIX, location.priority
        )
    )
 
 
def register(api_object, **kw):
    '''Register location with *session*.'''

    if not isinstance(api_object, ftrack_api.Session):
        return
 
    if not os.path.exists(DISK_PREFIX) or not os.path.isdir(DISK_PREFIX):
        logger.error('Disk prefix {} does not exist.'.format(DISK_PREFIX))
        return

    logger.info('Listening to event.')

    
    #api_object.event_hub.subscribe(
    #    'topic=ftrack.api.session.configure-location',
    #    functools.partial(configure_location, api_object)
    #)
    
    api_object.event_hub.subscribe(
        'topic=ftrack.connect.application.launch',
        functools.partial(configure_location, api_object)
    )
    
    api_object.event_hub.subscribe(
        'topic=ftrack.action.launch',
        functools.partial(configure_location, api_object)
    )

if __name__ == "__main__":
    
    try:
        from . .config.config import FTRACK_API_KEY, FTRACK_API_USER, FTRACK_SERVER
    except:
        config_directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'config')
            )
        sys.path.append(config_directory)
        from config import FTRACK_API_KEY, FTRACK_API_USER, FTRACK_SERVER


    logging.basicConfig(level=logging.INFO)
    session = ftrack_api.Session(server_url=FTRACK_SERVER, api_user=FTRACK_API_USER, api_key=FTRACK_API_KEY, auto_connect_event_hub=True)
    register(session)

    session.event_hub.wait()