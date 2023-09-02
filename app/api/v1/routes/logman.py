'''
Routes to manage the logs in the api. 

manage_archive/{command}/
export_all_archives/
'''
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.email import BasicResponse
from app.api import deps 
from app import models, crud
from app.utils.api_logger import logzz
from app.utils.file_handler import filesys
from app.core import settings
import os

router = APIRouter()


@router.post('/manage-archive/{command}', 
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK
)
def manage_logs_archives(
    command: str,  
    current_user: models.User = Depends(deps.get_current_active_user)
)-> None:
    '''
    Adds a remote way to delete the logs, or the entire log directory.

    command:
      name of the archive dir to delete
      --all to delete them all
      --wipe to remove the entire log directory     
    '''
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    
    sub_dirs: list[str] = 'info,error,debug,warn'.split(',')
    status: str = f'{settings.LOG_ARCHIVE_DIRECTORY}/{command+"/" if command in sub_dirs else ""} '\
                  f' clear success. command: {command}'
    cleared: str = 'done'

    try:
       if command == '--all':                          # All the sub directories
           logzz.archive.clear_subs(sub_dirs)

       elif command == "--wipe":                       # Fuck it, nuke em from ./logs on down. 
          filesys.rmdir(settings.LOG_DIRECTORY)
          status = f'Totally wiped: {settings.LOG_DIRECTORY}'
          cleared = 'wiped'     
      
       elif command in sub_dirs and isinstance(command, str):
           logzz.archive.clear_subs([command])

       elif isinstance(command, list) :
           # loop over list and see if each item is a file or directory
           # if its a file, delete it, if its a directory, remove it.
           status = f'Removed multiple items: {command}'
           for item in command:
               if item in sub_dirs:
                   #dir
                   path = os.path.join(settings.LOG_ARCHIVE_DIRECTORY, item)
                   filesys.rmdir(path)
                   logzz.info( f"Remove Directory: {path}")
                   filesys.mkdir(path)
                   logzz.info( f"Remake Directory: {path}")
               else:
                   #file 
                   path = os.path.join(settings.LOG_DIRECTORY, item)
                   filesys.delete(path)              
                   logzz.create_logfile(path)           
                   logzz.info( f"Delete File: {path}")        
                   logzz.info(f"File remade: {path}")

       else:
           cleared = 'nope'                            # Do nada cause some stupid nonsensical command got through. 
           status = f'{settings.LOG_ARCHIVE_DIRECTORY} remains untouched.'
           
       # How to notify of results:
       if cleared == 'done':
            logzz.info(
                f"Cleared: {settings.LOG_ARCHIVE_DIRECTORY}/{command+'/' if command in sub_dirs else ''}\n"
                f"{logzz.stream.Prefix.INFO_PRE}  The command was: {command}"
            ) 
       elif cleared == 'wiped':
           # Need to respawn the directories so logs will work
           logzz.setup()           
           logzz.info(
                f"Totally wiped: {settings.LOG_DIRECTORY}\n"
                f"{logzz.stream.Prefix.INFO_PRE}  The command was: {command}"
            )       
       elif cleared == 'nope':
           logzz.info(
                f"No clearing took place in: {settings.LOG_ARCHIVE_DIRECTORY}\n"
                f"{logzz.stream.Prefix.INFO_PRE}  The command was: {command}"
            )     
       
           
    except Exception as exc:
        print("ERROR: Error deleting the archive directory.")
        status = "ERROR: Error deleting the archive directory."
        logzz.error(f"Could not delete the archive directories... Exc: {str(exc)}")

    return JSONResponse( {'status': status})
    


@router.get('/export-all-archives/', 
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK
)
def export_all_archives(    
    current_user: models.User = Depends(deps.get_current_active_user)
) -> None:
    '''
    This endpoint will facilitate the zip archiving of all the files in ./logs
    Once they are zipped... the download link will be returned to the client.
    The client has the option to delete the .zip file on download.     
    '''
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    status: str= 'Testing...'
    return JSONResponse( {'status': status})

