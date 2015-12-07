"""
Takes a JSON-format input file and converts it into the format produced by
David Abraham's implementation of the Saidman Generator, with an additional file
for altruists.
"""

class ConversionError(Exception):
    pass

import sys
import json
import pprint

def write_file(filename, n_donors, edges):
    EDGE_WEIGHT = 1
    with open(filename, "w") as f:
        f.write("{}\t{}\n".format(n_donors, len(edges)))
        for e in edges:
            f.write("{}\t{}\t{}\n".format(e[0], e[1], EDGE_WEIGHT))
        f.write("{}\t{}\t{}\n".format(-1, -1, -1))


def add_matches(edge_list, donor_element, donor_idx, patient_id_to_idx):
    if "matches" in donor_element:
        matches = donor_element["matches"]
        for match in matches:
            edge_list.append((donor_idx, patient_id_to_idx[match["recipient"]]))

def convert(infile, outfilebase):
    with open(infile, "r") as f:
        data_map = json.load(f)["data"]  # Read as map. We'll convert to an array
        donors = []
        altruists = []
        # Donors and patients may not be sequentially numbered. Therefore, we
        # convert from ID to index, which is numbered 0, 1, ...
        dd_idx = 0  # Directed donor index 
        ndd_idx = 0 # Non-directed donor index
        dd_id_to_idx = {} # Map from directed donor ID to index
        patient_id_to_idx = {} # Map from patient ID to index
        dd_edges = [] # Edges from pair to pair
        ndd_edges = [] # Edges from NDD to pair
        for key in data_map:
            if "altruistic" not in data_map[key] or not data_map[key]["altruistic"]:
                donors.append({"donor": dd_idx})
                if "sources" in data_map[key]:
                    sources = data_map[key]["sources"]
                    if len(sources)==1:
                        patient_id_to_idx[sources[0]] = dd_idx 
                    else:
                        raise ConversionError("Number of sources for donor {} should be 1"
                                .format(key))
                else:
                    raise ConversionError("Sources missing for donor {}".format(key))
                dd_id_to_idx[key] = dd_idx
                dd_idx += 1
        for key in data_map:
            if "altruistic" not in data_map[key] or not data_map[key]["altruistic"]:
                add_matches(dd_edges, data_map[key], dd_id_to_idx[key], patient_id_to_idx)
        for key in data_map:
            if "altruistic" in data_map[key] and data_map[key]["altruistic"]:
                altruists.append({"donor": ndd_idx})
                add_matches(ndd_edges, data_map[key], ndd_idx, patient_id_to_idx)
                ndd_idx += 1

    write_file(outfilebase + ".input", dd_idx, dd_edges)
    write_file(outfilebase + ".ndds", ndd_idx, ndd_edges)

if __name__=="__main__":
    if len(sys.argv) < 3:
        print "Please specify input filename, output file base name"
        sys.exit(1)
    else:
        infile = sys.argv[1]
        outfilebase = sys.argv[2]
        convert(infile, outfilebase)
