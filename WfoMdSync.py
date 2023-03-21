import src.wfo as wfo
import os.path
import re

print("\n--------------------------")
print("WFP PlantList Synchronizer")
print("--------------------------")


# where all the goodness is stored
data_dir = 'data/'  # ends in slash

# the file containing the root wfo id if we are in monographic mode
root_id_file_path = data_dir + 'root.id'

# the file containing the list of wfo ids if we are in floristic mode
checklist_file_path = data_dir + 'checklist.csv'

# Firstly check which mode we are in
# In monographic mode there is a root.id file in the data directory
# In floristic mode there is a checklist.csv file
# monographic trumps floristic
rootId = None
if os.path.exists(root_id_file_path):
    print(f"- Found root id file at {root_id_file_path}")
    file = open(root_id_file_path, 'r')
    rootId = file.read()
    print(f"- Found root WFO ID: {rootId}")
    file.close()
else:
    print(f"- No {root_id_file_path} file found")
    if os.path.exists(checklist_file_path):
        print(f"- Found checklist file at {checklist_file_path}")
    else:
        print(f"- No checklist file found at {checklist_file_path} file found")
        response = input(
            f"- Enter a valid WFO ID to initialise the data in monographic mode or 'q' two quit: ")
        response = response.strip()
        if re.match("^wfo-[0-9]{10}$", response):
            print(
                f"- {response} is a well formed WFO ID")
            file = open(root_id_file_path, 'w')
            wfo_id = file.write(response)
            file.close()
            print(
                f"- {root_id_file_path} created")
            rootId = response
        else:
            print(
                f"Please either add a root.id file or checklist.csv file to the {data_dir} folder and try again.\n")
            exit()

# offer to zip up the data director
# FIXME

# indicate what mode we are in
if rootId:
    print("- Monographic mode")
    wfo.synchronizeFromRoot(rootId, data_dir)
else:
    print("- Floristic mode")
