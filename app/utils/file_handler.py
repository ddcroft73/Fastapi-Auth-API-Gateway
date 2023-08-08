from pathlib import Path
import shutil

'''
An extra layer used for all actions associated with the file system. 
'''

class CreateDirectoryError(Exception):
    pass

class RemoveDirectoryError(Exception):
    pass

class FileWriteError(Exception):
    pass

class FileDeleteError(Exception):
    pass

class FileReadError(Exception):
    pass

class FileMoveError(Exception):
    pass

class FileRenameError(Exception):
    pass


class FileHandler():

    def get_contents(self, file_name: str) -> str:
        '''
        Will return the contents of a file in a string.
        '''
        try:
            with open(file_name, 'r') as f:
                data: str = f.read()
            return data
        
        except FileNotFoundError:
            raise FileExistsError(f'Cannot find: {file_name}')
        
        except Exception as exc:
            raise FileReadError(
                f'An Error occured trying to read: {file_name}.\n {str(exc)}'
            )
            

    def mkdir(self, directory: str) -> None:
        '''
        Will create a directory at the given Path. Will create any parent directories that do not exist.
        Will not raise an exception if the directory already exists. Just steps away.
        
        I've modified it to return exists or created to let the program know the status.
        Its really just fluff. an excuse touse a nifty ternary operation.
        '''
        try:
            if Path(directory).exists():
                return 'exists'
            
            Path(directory).mkdir(parents=True, exist_ok=True)
            return 'created'
        
        except Exception as exc:
            raise CreateDirectoryError(
                f"An error occured attempting to create the directory: {directory}\n{str(exc)}"
            )
        
    def rmdir(self, directory: str) -> None:
        '''
        Will remove the given path. If there arefilesorsub directories in the path,
        They will be removed with no warnings or messages. Only responses will be on failure.
        '''
        try:
            shutil.rmtree(directory)

        except FileNotFoundError:
            # If the directory does not exist, just persist, salright! 
            pass
        
        except Exception as exc:
            raise RemoveDirectoryError(
                f'The following error occured trying to remove a directory: {str(exc)} '
            )
        

    def write(self, file_name: str, data: str, mode: str) -> None:
        '''
        Writes data to a file. THe mode is adjustable so append, overwrite. All fairgame. 
        '''
        try:
            with open(file_name, mode) as f:
                f.write(data)

        except Exception as exc:
            raise FileWriteError(
                f"The following error occured attempting to write to file: {file_name} in {mode} mode.\n{str(exc)}"
            )        
        
    def rename(self, old_filename: str, new_filename: str) -> None:
        try:
            current_file_path = Path(old_filename)
            new_file_path = Path(new_filename)
            current_file_path.rename(new_file_path)

        except Exception as exc:
            raise FileRenameError(
                f'The following error occured tryong to rename {old_filename} to {new_filename}\n{str(exc)}'
            )

    def delete(self, file_name: str) -> None:
        '''
        Deletes a file in the given path. No response unless in the event of a failure.
        '''
        if self.exists(file_name):
            try:
               Path(file_name).unlink()

            except FileNotFoundError:
               raise FileDeleteError(f'The file {file_name} does not exist.')
            
            except Exception as exc:
                raise FileDeleteError(
                    f'The following error occured while attempting to delete a file: {str(exc)}'
                )
            
    
    def exists(self, file_name: str) -> bool:
        '''
        Checks the existence of the file in the path. True if it lives, False if not. 
        '''
        if not Path(file_name).exists():
            return False
        return True

    def copy(self, old_locale: str, new_locale: str)-> None:    
        '''
        Will copy a file from one location to another, only if it exists.
        '''    
        if self.exists(old_locale):
            shutil.copy(old_locale, new_locale)        
        else:
            raise FileNotFoundError(
                f'The file: {old_locale} could not be found.\nCopy process terminated.'
            )    
    
    def move(self, old_locale: str, new_locale: str)-> None:
        '''
        Will move, the old copy will be deleted. A file from one spot to another, if it exists.
        '''
        if self.exists(old_locale):
            try:
               shutil.move(old_locale, new_locale)
               
            except Exception as e:
                raise FileMoveError(
                    f'The following error occured in the process of moving: {old_locale}\n{str(e)}'
                )   
        else:
            raise FileNotFoundError(
                f'The file: {old_locale} could not be found.\nCopy process terminated.'
            )    
    

filesys = FileHandler()