import json




def read_in(filename):
    with open(filename, "r") as file:
        return json.load(file)


def write_out(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)






def add_transitives(objects):
    for obj in objects:
        relations = {rel: {} for rel in ["above", "below", "right of", "left of", "ahead", "behind"]}
        for edge in obj["edges"]:
            rel = edge["relationship"]
            if rel != "connected":
                if edge["source"] not in relations[rel]:
                    relations[rel][edge["source"]] = set()
                relations[rel][edge["source"]].add(edge["target"])
        for rel_type, rel_data in relations.items():
            keys = list(rel_data.keys())
            for key in keys:
                targets = list(rel_data[key])
                for target in targets:
                    if target in relations[rel_type]:
                        for extended_target in relations[rel_type][target]:
                            if extended_target not in relations[rel_type][key]:
                                relations[rel_type][key].add(extended_target)
                                obj["edges"].append({
                                    "source": key,
                                    "target": extended_target,
                                    "relationship": rel_type
                                })




def add_opposites(objects):
    opposite = {
        "above": "below",
        "below": "above",
        "right of": "left of",
        "left of": "right of",
        "ahead": "behind",
        "behind": "ahead",
        "connected": "connected"
    }
    for obj in objects:
        new_edges = []
        for edge in obj["edges"]:
            rel = edge["relationship"]
            if rel in opposite:
                new_edge = {"source": edge["target"], "target": edge["source"], "relationship": opposite[rel]}
                if new_edge not in obj["edges"] and new_edge not in new_edges:
                    new_edges.append(new_edge)
        obj["edges"].extend(new_edges)





def remove_rel_dups(data):
    for obj in data:
        unique_edges = set()
        new_edges = []
        for edge in obj["edges"]:
            edge_tuple = (edge["source"], edge["target"], edge["relationship"])
            if edge_tuple not in unique_edges:
                unique_edges.add(edge_tuple)
                new_edges.append(edge)
        obj["edges"] = new_edges





def main():
    filename = "obj_data.json"
    data = read_in(filename)
    add_transitives(data)
    add_opposites(data)
    remove_rel_dups(data)
    write_out(data, filename)

if __name__ == "__main__":
    main()

#===============================================================================
