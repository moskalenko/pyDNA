#~~~~~~~GLOBAL IMPORTS~~~~~~~#

# Standard library packages import
from os import remove, path
import gzip
from time import time
from sys import stdout

# Third party package import
from Bio import SeqIO

# Local library packages import
from Utilities import import_seq, file_basename, mkdir
from Blast import Blastn

#~~~~~~~MAIN METHODS~~~~~~~#

def mask (  subject_fasta,
            hit_list,
            ref_outdir="./references/",
            ref_outname="masked_ref.fa",
            compress_ouput=True ):
    """
    Import a reference fasta sequence, Mask positions indicated by hits from a hit_list and write
    the modified fasta sequence in a new file.
    @param subject_fasta Fasta sequence of the subject to edit (can be gzipped)
    @param hit_list List of hit objects. Hits need at least 3 fields named s_id, s_start and s_end
    coresponding to the name of the sequence matched, and the hit start/end (0 based).
    @param ref_outdir Directory where the masked reference will be created
    @param ref_outname Name of the masked reference
    @return A path to the modified sequence if the hit list was valid.
    """

    # Test if object the first object of hit_list have the require s_id, s_start and s_end fields
    try:
        a = hit_list[0].s_id
        a = hit_list[0].s_start
        a = hit_list[0].s_end

    except (IndexError, AttributeError) as E:
        print (E)
        print ("The hit_list does not contain suitable hit objects or is empty")
        print ("The subject fasta file will not be edited")
        return subject_fasta

    # Initialize output folder
    mkdir(ref_outdir)

    # Initialize input fasta file
    if subject_fasta[-2:].lower() == "gz":
        in_handle = gzip.open(subject_fasta, "r")
    else:
        in_handle = open(subject_fasta, "r")

    # Initialize output fasta file
    if compress_ouput:
        ref_path = path.join (ref_outdir, ref_outname+".gz")
        out_handle = gzip.open(ref_path, 'w')
    else:
        ref_path = path.join (ref_outdir, ref_outname)
        out_handle = open(ref_path, 'w')

    # Generate a list of ref that will need to be modified
    id_list = {hit.s_id:0 for hit in hit_list}.keys()

    # Iterate over record in the subject fasta file
    print ("\nMasking hit positions and writting a new reference".format(
        file_basename (subject_fasta)))
    # Iterate over record in the subject fasta file
    i=j=0
    start_time = time()
    for record in SeqIO.parse(in_handle, "fasta"):
        # Progress Marker
        stdout.write(".")
        stdout.flush()

        # Check if the record is in the list of record to modify
        if record.id in id_list:
            i+=1
            #~print ("Hit found in {}. Editing the sequence".format(record.id))
            # Casting Seq type to MutableSeq Type to allow string editing
            record.seq = record.seq.tomutable()

            # For each hit in the list of hit found
            for hit in hit_list:
                if record.id == hit.s_id:

                    # For all position between start and end coordinates modify the base by N
                    for position in range (hit.s_start, hit.s_end+1):
                        record.seq[position]= 'N'
        else:
            j+=1
            #~print ("No hit found in {}".format(record.id))

        # Finally write the sequence modified or not
        out_handle.write(record.format("fasta"))

    # Report informations
    print("\nNew reference file {} created".format(ref_outname))
    print("{} Sequence processed of which {} sequences modified".format(i+j,i))
    print("Execution time : {}s\n".format(round(time()-start_time),2))

    # Close files and return the masked ref path
    in_handle.close()
    out_handle.close()
    return ref_path
