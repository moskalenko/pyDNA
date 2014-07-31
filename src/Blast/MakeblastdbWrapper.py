#~~~~~~~GLOBAL IMPORTS~~~~~~~#
# Standard library packages import
import os, gzip
from time import time
from tempfile import mkstemp

# Local library packages
from Utilities import run_command, file_basename, make_cmd_str, fgunzip

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
class NewDB(object):
    """
    @class NewDB
    @brief Wrapper for makeblastdb index. Create a subject database from a fasta file.
    Blast+ 2.8+ needs to be install and correctly added to the path.
    """
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~FONDAMENTAL METHODS~~~~~~~#

    def __repr__(self):
        msg = self.__str__()
        msg += "Makeblastdb path : {}\n".format(self.makeblastdb)
        msg += "Blastn database path : {}\n".format(self.db_path)
        msg += "Options :\n"
        for i, j in self.makeblastdb_opt.items():
            msg += "\tFlag : {}\tValue : {}\n".format(i,j)
        return msg

    def __str__(self):
        return "\n<Instance of {} from {} >\n".format(self.__class__.__name__, self.__module__)

    def __init__ (self, ref_path, db_path="./out", makeblastdb_opt=None, makeblastdb="makeblastdb"):
        """
        Create a blastdb from a reference fastq file
        @param ref_path Path of the fasta file containing the reference sequence. Can be gzipped
        but in this case the compressed file will be extracted in a temporary file
        @param db_path Outname for the blast db files basename.
        @param makeblastdb_opt makeblastdb dictionnary of option arguments such as "-t 5". The option flag
        have to be the key (without "-") and the the option value in the dictionnary value. If no
        value is requested after the option flag "None" had to be asigned to the value field.
        @param makeblastdb Path ot the makeblastdb executable. If blast+ if already added to your
        system path do not change the default value
        """
        # Creating object variables
        self.makeblastdb = makeblastdb
        self.db_path = db_path
        self.db_name = file_basename(ref_path)

        # init an option dict and attribute defaut options
        self.makeblastdb_opt = index_opt if makeblastdb_opt else {}
        self.makeblastdb_opt["out"] = self.db_path
        self.makeblastdb_opt["dbtype"] = "nucl"
        self.makeblastdb_opt["input_type"] = "fasta"

        try:
            #### TO DO = Check that their is no memory leak here
            # If the fasta file is compressed = extract the file in a tempory file
            if ref_path[-2:].lower() == "gz":
                print ("Extracting the compressed fasta in a temporary file")
                fd, tmp_path = mkstemp()
                fgunzip (in_path=ref_path, out_path=tmp_path)
                self.makeblastdb_opt["in"] = tmp_path
                self._make_db()
                os.close(fd)
                os.remove(tmp_path)

            # Else just proceed by using the fasta reference
            else:
                self.makeblastdb_opt["in"] = ref_path
                self._make_db()

        except Exception as E:
            self._remove_db_files()
            raise Exception (E.message+"Impossible to generate a valid database from the reference sequence")

        else:
            print ("\tDatabase ready")

    #~~~~~~~PRIVATE METHODS~~~~~~~#

    def _make_db(self):
        """
        Create a blastn database from ref_path using makeblastdb
        """
        # Build the command line thanks to make_cmd_str
        cmd = make_cmd_str(self.makeblastdb, self.makeblastdb_opt)
        print "Creating a blastn database for {}".format(self.db_name)
        # Run the command line without stdin and asking both stdout and stderr
        start_time = time()
        stdout, stderr = run_command(cmd, stdin=None, ret_stderr=True, ret_stdout=True)

        # Verify the output
        if not stdout:
            raise Exception ("Error, no data received from standard output\n"+stderr)

        #print (stdout)
        print ("Database created in {}s".format(round(time()-start_time, 3)))

    def _remove_db_files(self):
        """
        Remove db files in case of exception during db creation
        """
        print("Remove database files")

        # Removing DB file
        for ext in ["00.nhr", "nhr", "00.nin", "nin", "00.nsq", "nsq"]:
            f = "{}.{}".format(self.db_path, ext)
            if path.isfile (f):
                remove (f)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
class ExistingDB(object):
    """
    @class ExistingDB
    @brief Import an existing blastn database + verify the existence of files
    """
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def __repr__(self):
        msg = self.__str__()
        msg += "Blastn database path : {}\n".format(self.db_path)
        return msg

    def __str__(self):
        return "\n<Instance of {} from {}>\n".format(self.__class__.__name__, self.__module__)

    def __init__ (self, db_path):
        """
        @param db_path The db path is the name of any of the db files up to but not including the
        final "nhr", "nin" or "nsq"
        """
        # Creating object variables
        self.db_path = db_path

        print ("Checking db files")
        # Checking if all index files needed by bwa are
        for ext in ["nhr", "nin", "nsq"]:
            f = "{}.{}".format(self.db_path, ext)

            if not path.isfile (f):
                raise Exception ("Invalid database : {} does not exist".format(f))
            if path.getsize(f) == 0:
                raise Exception ("Invalid database : {} is empty".format(f))

        print ("All index files are valid")
