from pathlib import Path
from datetime import datetime, time, timedelta
import re
from os.path import join as os_join
from .file_handler import filesys


"""
API Logger - 

This is just a simple way to add a display, if you will, to my APIS. THe nature of a web API doesnt allow you to
get any decent feedback from the terminal. This little module is compact and it simply allows 
you to insert log entries anywhere you want and they will be kept in organized files. You can set the 
Line size of the log files, and once that ceiling is realoized, the logs will be exported and organized into
an archive location. Do not confuse this with theway the Python logger works. I opted to use "Streams" and not
set levels. A stream is just a file that contains a certain type of log entry. 
The Log locations are set in logger.settings. and default to the cwd. It will put the logs/ into the same directory
as your entrypoint. main.py in this demo.
"""

class Stream():
    INFO: int = 10
    DEBUG: int = 20
    ERROR: int = 30
    WARN: int = 40
    INTERNAL: int = 50
    LOGIN: int = 60

    class Prefix():
        INFO_PRE: str =  "INFO: "
        DEBUG_PRE: str = "DEBUG: "
        ERROR_PRE: str = "ERROR: "
        WARN_PRE: str =  "WARNING: "
        INTERNAL_PRE: str= '[ INTERNAL ]'
        LOGIN_PRE: str = "LOGIN: "

class DateTime():

    @staticmethod
    def date_time_now() -> tuple[str]:
        """returns the formatted date and time in a tuple"""
        current_time: time = datetime.now()
        formatted_time: str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        _date: str = formatted_time.split()[0]
        _time: str = formatted_time.split()[1]
        return (_date, _time)
    
    @staticmethod
    def timedelta() -> timedelta:
        return timedelta
        

class ScreenPrinter():
    def to_screen(self, message: str) -> None:
        print(message)



class Archive():
    """
    How the archiving will work:

    The maximum size of a log file is set at 1000 lines. This may need to be adjusted. If the class is instantiated
    with 'archive_log_files = True, then whenever a file reaches the max it will be moved to the archive and a new one
    will be created in its place.

    1. a call is made to Archive.archive_logfile()
    2. rename the current logfile using the info in the first line.
    3. move the newly named file into the archive.

    """

    class ArchiveSubDirectories():
        DEBUG_DIR: str = "debug"
        INFO_DIR: str = "info"
        WARN_DIR: str = "warn"
        ERROR_DIR: str = "error"
        LOGIN_DIR: str = "login"

        @classmethod
        def to_list(cls) -> list:
            '''
            Levearages vars() to extract the values of each attribute into 
            an iterable.
            '''
            attributes = vars(cls)
            directories = [
                value
                for name, value in attributes.items()
                if isinstance(value, str) and name != "__module__"
            ]
            return directories


    def __init__(self, archive_directory: str, ):
        """
        Archive
        """
        self.archive_directory = archive_directory
        self.create_archive_sub_directories()


    def clear_subs(self, subs: list[str]) -> None:
        '''
        Will delete one or more of the archive sub directories. once done it recreates whatever isnt there
        This sub is meant to clear the directories not delete and leave it. 
        '''
        for sub in subs:
            filesys.rmdir(os_join(self.archive_directory, sub))
            logzz.internal(Stream.Prefix.INFO_PRE,f"Deleted: {os_join(self.archive_directory, sub)}")

        # Rebuild the archive directories... we are just clearing not deleting. They ned to be 
        # present incase an archive needs to take place. 
        self.create_archive_sub_directories()
        logzz.internal(Stream.Prefix.INFO_PRE, f'func: clear_subs() Recreated Sub Directories')
        
    def create_archive_sub_directories(self) -> None:
        """
        Creates the sub directories to house the archived logs.
        """
        for sub in self.ArchiveSubDirectories.to_list():
            state: str = filesys.mkdir(os_join(self.archive_directory, sub))
            msg: str = (
                "was " if state == "created" else "already"
            )
            # print(f"Sub directory: '{sub}' {msg} {state}.")
        
    def get_line_cnt(self, file_name: str) -> int:
        """
        """
        file_lines: list[str] = filesys.get_contents(file_name).split("\n")
        return len(file_lines)

    def get_sub_directory(self, stream: int) -> str:
        '''
        Returns the Sub directory associated to the stream. 
        '''
        sub_dir: str = ""
        if stream == Stream.INFO:
            sub_dir = self.ArchiveSubDirectories.INFO_DIR
        elif stream == Stream.ERROR:
            sub_dir = self.ArchiveSubDirectories.ERROR_DIR
        elif stream == Stream.WARN:
            sub_dir = self.ArchiveSubDirectories.WARN_DIR
        elif stream == Stream.DEBUG:
            sub_dir = self.ArchiveSubDirectories.DEBUG_DIR
        elif stream == Stream.LOGIN:
            sub_dir = self.ArchiveSubDirectories.LOGIN_DIR
        return sub_dir
    #
    # Think about error handling in this method??
    #
    def archive_logfile(self, logfile: str, stream: int) -> None:
        """
            Moves the logfile from its old location to a new location after renaming .
            Creates a new logfile in its place and image.
            1. rename the current logfile. 
            2. Move the file to the appropriate archive directory.             """

        def get_new_filename(filename: str) -> str:
            '''
            Using the string of text prepended at the top of each log, Pull out the time
            and date (via extract_date_time_from_string())to be used in naming the log 
            file in the archive. 
            '''
            def extract_date_time_from_string(input_string: str) -> tuple[str] | str:
                datetime_pattern = r"\b(\d{4}-\d{2}-\d{2}) @ (\d{2}:\d{2}:\d{2})\b"
                match = re.search(datetime_pattern, input_string)
                if match:
                    return match.group(1), match.group(2)
                else:
                    return "no_date_time"

            # get the first line from the log file.
            date_time_string: str = filesys.get_contents(filename).split("\n")[0]
            date, time = extract_date_time_from_string(date_time_string)
            orig_directory: str = "./" + filename.split("/")[1]
            fname_with_ext: str = filename.split("/")[-1]
            fname_no_ext: str = fname_with_ext.split(".")[0]

            return (
                f"{orig_directory}/{fname_no_ext}_{date}_{time}.log",
                f"{fname_no_ext}_{date}_{time}.log",
            )

        # Rename the current logfile.
        new_logfile_path, new_logfile_only = get_new_filename(logfile)
        filesys.rename(logfile, new_logfile_path)
        
        # select right logfile type to store it.
        sub_dir: str = self.get_sub_directory(stream)
        current_location: str = new_logfile_path
        archive_location: str = f'{self.archive_directory}/{sub_dir}/{new_logfile_only}'

        # Move it to its appropriate sub directory.
        filesys.move(current_location, archive_location)
        
        # Use the instance of the APILogger               
        logzz.internal(
            Stream.Prefix.INFO_PRE, 
            f'Archiving the INFO logfile.      File size: {logzz.log_file_max_size} lines.'
        )

    def set_archive_directory(self, directory: str) -> None:
        """Will create the main directory for all logfiles to be archived to."""
        try:
            filesys.mkdir(directory)

        except Exception as exc:
            logzz.internal(
                Stream.Prefix.ERROR_PRE, 
                f"func: Archive.set_archive_directory() \n{str(exc)}"
            )
            

class APILogger():   

    LOG_DIRECTORY: str = "./logs"   
    LOG_ARCHIVE_DIRECTORY: str = "./logs/log-archives"
    DEFAULT_LOG_FILE: str = "./logs/DEFAULT-app-logs.log"

    def __init__(
        self,
        info_filename: str = None,
        error_filename: str = None,
        warning_filename: str = None,
        debug_filename: str = None,
        login_filename: str = None,
        archive_log_files: bool = True,
        log_file_max_size: int = 1000,
    ) -> None:
        self.stream = Stream()
        self.archive = Archive(
            archive_directory=self.LOG_ARCHIVE_DIRECTORY
        )
        self.d_and_t = DateTime()
        self.prnt = ScreenPrinter()

        # file to log internal messages: This is by default, since it would be difficult to ever see any errors 
        # the server may encounter, they are all remanded to the internal.log file. 
        self.internal_filename = 'internal.log'

        self.info_filename = info_filename
        self.error_filename = error_filename
        self.warning_filename = warning_filename
        self.debug_filename = debug_filename
        self.login_filename = login_filename
        self.archive_log_files = archive_log_files 
        self.log_file_max_size = log_file_max_size    # DEBUGING=5      

        self.__handle_file_setup()
    
    def setup(self) -> None:
        self.__handle_file_setup()
        
    def __handle_file_setup(self) -> None:
        """
        Handles the creation of any user defined logfiles, the Default
        log file, and the vreation of the archive directory to be used when archiving
        excess lof files.
        """
        if self.archive_log_files:
            self.archive.set_archive_directory(self.LOG_ARCHIVE_DIRECTORY)

        file_names = [
            self.info_filename,
            self.error_filename,
            self.warning_filename,
            self.debug_filename,
            self.internal_filename,
            self.login_filename
        ]

        for file_name in file_names:
            if file_name is not None:
                self.__set_log_filename(os_join(self.LOG_DIRECTORY, file_name))

        if any(filename is None for filename in file_names):
            self.__set_log_filename(self.DEFAULT_LOG_FILE)

    #
    # __save_log_entry().
    #   
    def __save_log_entry(
            self,  
            message: str, 
            stream: int, 
            timestamp: bool, 
            file_name: str
    ) -> None:
        '''
        
        '''
        def prep_N_format(file_name: str, message: str):
            """
            last chance to set the filename, add timestamp if applicablew
            and \n final touches.
            """
            if file_name is None or file_name == "None":
                file_name = self.DEFAULT_LOG_FILE
            else:
                file_name = os_join(self.LOG_DIRECTORY, file_name)

            if timestamp:
                date_time: str = f"{self.d_and_t.date_time_now()[0]} {self.d_and_t.date_time_now()[1]}"
                message = f"{message} § [{date_time}]\n"
            else:
                message += "\n"

            return (file_name, message)


        def commit_message(message: str, file_name: str) -> None:
            """
            Handles writing log entries to the corresponding file.
            With the helpof a class created just to deal with the file system
            """
            try:
                filesys.write(file_name, message, mode="a")

            except Exception as exc:
                logzz.internal(
                    Stream.Prefix.ERROR_PRE,
                    f"func: commit_message() \n"
                    f"Check path and spelling. \n {str(exc)}"
                )

        # Sometimes message may be None or a dict. Just represent them in string form. 
        if message == None: message = "None"
        if isinstance(message, dict):
            message = str(message)        

        logfile, message = prep_N_format(
            file_name=file_name, 
            message=message
        )
        #
        # Before Writiing to the file, check its size to see if it's time to archive it.
        #
        if self.archive.get_line_cnt(logfile) >= self.log_file_max_size:
            self.archive.archive_logfile(logfile=logfile, stream=stream)            
            # create new log file in place of the other, with the original name
            self.__set_log_filename(logfile)

        commit_message(message, logfile)


    def print2_screen(self, message: str, stream: int, timestamp: bool) -> None:
        """two guesses..."""
        msg_prefix: str

        if stream == Stream.INFO:
            msg_prefix = Stream.Prefix.INFO_PRE
        elif stream == Stream.WARN:
            msg_prefix = Stream.Prefix.WARN_PRE
        elif stream == Stream.DEBUG:
            msg_prefix = Stream.Prefix.DEBUG_PRE
        elif stream == Stream.ERROR:
            msg_prefix = Stream.Prefix.ERROR_PRE
        elif stream == Stream.LOGIN:
            msg_prefix = Stream.Prefix.LOGIN_PRE
        elif stream == 0:
            msg_prefix=""

        if timestamp:
            date_time: str = f"{self.d_and_t.date_time_now()[0]} {self.d_and_t.date_time_now()[1]}"
            message = f"{message} § [{date_time}]"   

        self.prnt.to_screen(f"{msg_prefix}{message}")

    #
    # Log Message Interfaces
    #
    def error(self, message: str, timestamp: bool = False) -> None:
        message = f"{Stream.Prefix.ERROR_PRE} {message}"
        self.__save_log_entry(
            message,
            Stream.ERROR,
            timestamp,
            self.error_filename
        )       

    def info(self, message: str, timestamp: bool = False) -> None:
        message = f"{Stream.Prefix.INFO_PRE} {message}"
        self.__save_log_entry(
            message,
            Stream.INFO,
            timestamp,
            self.info_filename
        )               

    def warn(self, message: str, timestamp: bool = False) -> None:
        message = f"{Stream.Prefix.WARN_PRE} {message}"
        self.__save_log_entry(
            message,
            Stream.WARN,
            timestamp,
            self.warning_filename
        )       

    def debug(self, message: str, timestamp: bool = False) -> None:
        message = f"{Stream.Prefix.DEBUG_PRE} {message}"
        self.__save_log_entry(
            message,
            Stream.DEBUG,
            timestamp,
            self.debug_filename
        )  

    def login(self, message: str, timestamp: bool = False) -> None:
        message = f"{Stream.Prefix.LOGIN_PRE} {message}"
        self.__save_log_entry(
            message,
            Stream.LOGIN,
            timestamp,
            self.login_filename
        )      

    def internal(self, stream2: int, message: str, timestamp: bool = False) -> None:
        # Brand the message
        message = f'{Stream.Prefix.INTERNAL_PRE}  {stream2} {message}'
        self.__save_log_entry( 
            message, 
            Stream.INTERNAL, 
            timestamp, 
            self.internal_filename
        )

    # This just became a seperate Stream. I feel I'd have been remiss 
    # if not including some method to print to screen. 
    def print(self, message: str, stream: int=0, timestamp: bool=False):
        self.print2_screen(message, stream, timestamp)

    def create_logfile(self, filename: str) -> None:
        self.__set_log_filename(filename)
    

    def __set_log_filename(self, file_name: str) -> None:
        """This method creates the initial file. If a file already exists, it does nada.
        Sets up the logfile.
        """
        date, time = self.d_and_t.date_time_now()    
        header: str = (
            f" [ {file_name} ] created on {date} @ {time}\n\n"
        )
        if Path(file_name).exists():
            return

        try:
            filesys.write(file_name, header, "w")

        except Exception as e:
            logzz.internal(
                Stream.Prefix.ERROR_PRE,
                " func:  __set_log_filename() "
            )


logzz = APILogger(
    info_filename="INFO_logzz.log",
    debug_filename="DEBUG_logzz.log",
    error_filename="ERROR_logzz.log",
    warning_filename=None,
    login_filename="LOGIN_logzz.log",
    archive_log_files=True,
    log_file_max_size=1000,
)
