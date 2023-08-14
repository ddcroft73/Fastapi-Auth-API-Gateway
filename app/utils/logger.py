from pathlib import Path
from datetime import datetime, time, timedelta
import re
from os.path import join as os_join
from .file_handler import filesys
from app.core import settings


"""
#
# "EZ Logger class.
# 
This is not like the Python logger. It Allows me to save messsages defined by a certain level, but it doesnt have to
have a level set to log anything. Its just a way to give the backend an inerface and allows me to log everything that
happens, that i want to log. The logs are kept in a folde you choose and they will auto archive when a certainsize is realized
THis way i can go back if there is a problem and look throigh all the back logs that are kept neat and in managable
"piles'

it lets me log 
ERRORS
DEBUG
INFO
WARNNG

All you have to do is call the type log you weant to save. logger.info("Message") and it goes with all the info logs
Same with the other types. You dont have to worry about much configuring. If you dont select names for the log files
It will add them all to a defalt log file.  
"""

class ScreenPrinter:
    def __init__(self):
        print("ScreenPrinter class... created.")

    def to_screen(self, message: str) -> None:
        print(message)


class EZLogger:
    class DateTime:
        def __init__(self):
            print("DateTime class... created")

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
        
    class Archive:
        """
        How the archiving will work:

        The maximum size of a log file is set at 1000 lines. This may need to be adjusted. If the class is instantiated
        with 'archive_log_files = True, then whenever a file reaches the max it will be moved to the archive and a new one
        will be created in its place.

        1. a call is made to Archive.archive_logfile()
        2. rename the current logfile using the info in the first line.
        3. move the newly named file into the archive.
        
        """

        class ArchiveSubDirectories:
            DEBUG_DIR: str = "debug"
            INFO_DIR: str = "info"
            WARN_DIR: str = "warn"
            ERROR_DIR: str = "error"

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


        def __init__(self, archive_directory: str, Level):
            """
            Most of this class is justma skeleton for now.
            """
            self.archive_directory = archive_directory
            self.Level = Level
            self.create_archive_sub_directories()

            print("Archive class... created")

        def clear_subs(self, subs: list[str]) -> None:
            '''
            Will delete one or more of the archive sub directories. once done it recreates whatever isnt there
            This sub is meant to clear the directories not delete and leave it. 
            '''
            for sub in subs:
                filesys.rmdir(os_join(self.archive_directory, sub))
                print(f"Deleted: {os_join(self.archive_directory, sub)}")

            # Rebuild the archive directories... we are just clearing not deleting.
            self.create_archive_sub_directories()
            print(f'func: clear_subs() Recreated Sub Directories')
            
        def create_archive_sub_directories(self) -> None:
            """
            Creates the sub directories to house the archived logs.
            If they already exist, nothing is done but a flag is returned to specify
            It exists. If it does not exist, it is created and a flag is returned saying it
            was just created... (This was really only done so I could use this nifty ternary
            operation I came up with.)
            """
            for sub in self.ArchiveSubDirectories.to_list():
                state: str = filesys.mkdir(os_join(self.archive_directory, sub))
                msg: str = (
                    "was " if state == "created" else "already"
                )
                print(f"Sub directory: '{sub}' {msg} {state}.")
            
        def get_line_cnt(self, file_name: str) -> int:
            """
               1. get contents of the file. 
               2. convert to list. 
               3. return the total items in list.
            """
            file_lines: list[str] = filesys.get_contents(file_name).split("\n")
            return len(file_lines)

        def get_sub_directory(self, level: int) -> str:
            '''
            Returns the Sub directory associated to the level. 
            '''
            sub_dir: str = ""
            if level == self.Level.INFO:
                sub_dir = self.ArchiveSubDirectories.INFO_DIR

            elif level == self.Level.ERROR:
                sub_dir = self.ArchiveSubDirectories.ERROR_DIR

            elif level == self.Level.WARN:
                sub_dir = self.ArchiveSubDirectories.WARN_DIR

            elif level == self.Level.DEBUG:
                sub_dir = self.ArchiveSubDirectories.DEBUG_DIR

            return sub_dir
        #
        # Think about error handling in this method??
        #
        def archive_logfile(self, logfile: str, level: int) -> None:
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
            new_logfile_full, new_logfile_only = get_new_filename(logfile)
# SAFETY    filesys.rename(logfile, new_logfile_full)

            sub_dir: str = self.get_sub_directory(level)
            current_location: str = new_logfile_full
            archive_location: str = f'{self.archive_directory}{sub_dir}{new_logfile_only}'

            # Move it to its appropriate sub directory.
# SAFETY    filesys.move(current_location, archive_location)

            print(f"\nRenamed: {logfile} to: {new_logfile_full}")
            print(f"\nMoved: {current_location} TO: {archive_location}"            )

        def set_archive_directory(self, directory: str) -> None:
            """Will create the main directory for all logfiles to be archived to."""
            try:
                filesys.mkdir(directory)
            except Exception as exc:
                print(f"func: Archive.set_archive_directory() \n{str(exc)}")


    INFO_PRE: str = "INFO: "
    DEBUG_PRE: str = "DEBUG: "
    ERROR_PRE: str = "ERROR: "
    WARN_PRE: str = "WARNING: "
   # LOGIN_PRE: str ="LOGIN INFO"

    FILE: int = 0
    SCREEN: int = 1
    BOTH: int = 2

    class Level:
        INFO: int = 10
        DEBUG: int = 20
        ERROR: int = 30
        WARN: int = 40
       # LOGIN: int = 50
    
    LOG_DIRECTORY: str = settings.LOG_DIRECTORY    
    LOG_ARCHIVE_DIRECTORY: str = settings.LOG_ARCHIVE_DIRECTORY
    DEFAULT_LOG_FILE: str = settings.DEFAULT_LOG_FILE

    def __init__(
        self,
        info_filename: str = None,
        error_filename: str = None,
        warning_filename: str = None,
        debug_filename: str = None,
        output_destination: str = FILE,
        archive_log_files: bool = True,
        log_file_max_size: int = 1000,
    ) -> None:
        self.archive = self.Archive(
            archive_directory=self.LOG_ARCHIVE_DIRECTORY, 
            Level=self.Level
        )
        self.d_and_t = self.DateTime()
        self.prnt = ScreenPrinter()

        time_date: tuple[str] = self.d_and_t.date_time_now()        
        self.start_date: str = time_date[0] 
        self.start_time: str = time_date[1] 

        self.info_filename = info_filename
        self.error_filename = error_filename
        self.warning_filename = warning_filename
        self.debug_filename = debug_filename
        self.output_destination = output_destination  # FILE, SCREEN, or BOTH
        self.archive_log_files = archive_log_files 
        self.log_file_max_size = log_file_max_size    # DEBUGING=5      

        self.__handle_file_setup()

    def __handle_file_setup(self) -> None:
        """
        Handles the creation of any user defined logfiles, the Default
        log file, and the vreation of the archive directory to be used when archiving
        excess lof files.
        """
        if self.archive_log_files:
            self.archive.set_archive_directory(self.LOG_ARCHIVE_DIRECTORY)

        if self.output_destination == self.FILE or self.output_destination == self.BOTH:
            file_names = [
                self.info_filename,
                self.error_filename,
                self.warning_filename,
                self.debug_filename,
            ]

            for file_name in file_names:
                if file_name is not None:
                    self.__set_log_filename(os_join(self.LOG_DIRECTORY, file_name))

            if any(filename is None for filename in file_names):
                self.__set_log_filename(self.DEFAULT_LOG_FILE)


    def __save_log(self, message: str, level: int, timestamp: bool) -> None:
        fname: str | None = None

        def add_final_touches(file_name: str, message: str):
            """
            last chance to set the filename, add timestamp if applicablew
            and \n final touches.
            """
            if file_name is None:
                file_name = self.DEFAULT_LOG_FILE
            else:
                file_name = os_join(self.LOG_DIRECTORY, file_name)

            if timestamp:
                date_time: str = f"{self.d_and_t.date_time_now()[0]} {self.d_and_t.date_time_now()[1]}"
                message = f"{message} § [{date_time}]\n"
            else:
                message += "\n"

            return (file_name, message)

        def ready_message(message: str) -> tuple[str]:
            """
            add a prefix to the message string, and reference
            the correct file to write to.
            """
            # If the message happens to come back as None. or its a dictionary,
            # modify the input so its reflected and does not choke.
            if message == None: message = "None"
            if isinstance(message, dict):
                message = str(message)
                
            if level == self.Level.INFO:
                file_name = self.info_filename
                message = self.INFO_PRE + message

            elif level == self.Level.WARN:
                file_name = self.warning_filename
                message = self.WARN_PRE + message

            elif level == self.Level.DEBUG:
                file_name = self.debug_filename
                message = self.DEBUG_PRE + message

            elif level == self.Level.ERROR:
                file_name = self.error_filename
                message = self.ERROR_PRE + message

            return (file_name, message)

        def commit_message(message: str, file_name: str) -> None:
            """
            Handles writing log entries to the corresponding file.
            With the helpof a class created just to deal with the file system
            """
            try:
                filesys.write(file_name, message, mode="a")

            except Exception as exc:
                print(
                    "ERROR: func: commit_message() There was an error attempting a write action on:\n"
                    f"{fname}\n"
                    f"Check path and spelling. \nHere go yo Exception: {str(exc)}"
                )

        # Finalize the logfile entry.
        fname, message = ready_message(message)
        fname, message = add_final_touches(file_name=fname, message=message)
        #
        # Before Writiing to the file, check its size to see if it's time to archive it.
        #
        if self.archive.get_line_cnt(fname) >= self.log_file_max_size:
            self.archive.archive_logfile(logfile=fname, level=level)
            # create new log file with the original name
            self.__set_log_filename(fname)
        #
        # Write to the logfile
        #
        commit_message(message, fname)


    def __print_screen(self, message: str, level: int, timestamp: bool) -> None:
        """two guesses..."""
        msg_prefix: str

        if level == self.Level.INFO:
            msg_prefix = self.INFO_PRE

        elif level == self.Level.WARN:
            msg_prefix = self.WARN_PRE

        elif level == self.Level.DEBUG:
            msg_prefix = self.DEBUG_PRE

        elif level == self.Level.ERROR:
            msg_prefix = self.ERROR_PRE
        
        if timestamp:
           message = message + f' § [{timestamp}]'

        self.prnt.to_screen(f"{msg_prefix}{message}")


    def __route_output(self, message: str, level: int, timestamp: bool = False) -> None:
        """
        Whenever a log message is invoked, this method will route the output to the proper direction(s)
        """

        if self.output_destination == self.FILE:
            self.__save_log(message, level, timestamp)

        elif self.output_destination == self.SCREEN:
            self.__print_screen(message, timestamp)

        elif self.output_destination == self.BOTH:
            self.__print_screen(message, level, timestamp)
            self.__save_log(message, level, timestamp)

    #
    # Log Message Interfaces
    #
    '''
    Before a write or any action that requires accessing the file system, I need to know if the ./log 
    directory integrity is still in tact. This could change if maintenece is carried out on one of the 
    directories or files. as simple as one letter in the name can cause havoc. 

    Before any file op takes place, just heck existence? if its not there, then create it to keep it from crashing?
    '''
    def error(self, message: str, timestamp: bool = False) -> None:
        self.__route_output(message, self.Level.ERROR, timestamp)

    def info(self, message: str, timestamp: bool = False) -> None:

        self.__route_output(message, self.Level.INFO, timestamp)

    def warning(self, message: str, timestamp: bool = False) -> None:
        self.__route_output(message, self.Level.WARN, timestamp)

    def debug(self, message: str, timestamp: bool = False) -> None:
        self.__route_output(message, self.Level.DEBUG, timestamp)



    def __set_log_filename(self, file_name: str) -> None:
        """This method creates the initial file. If a file already exists, it does nada.
        Sets up the logfile.
        """
        header: str = (
            f" [ {file_name} ] created on {self.start_date} @ {self.start_time}\n\n"
        )
        if Path(file_name).exists():
            return

        try:
            filesys.write(file_name, header, "w")

        except Exception as e:
            print(
                "ERROR: func:  __set_log_filename() There was an error attempting a write action on:\n"
                f"{file_name}\n"
                "Check path and spelling."
            )


logzz = EZLogger(
    info_filename="INFO_logzz.log",
    debug_filename="DEBUG_logzz.log",
    error_filename="ERROR_logzz.log",
    warning_filename=None,
    output_destination=EZLogger.FILE,
    archive_log_files=True,
    log_file_max_size=1000,
)
