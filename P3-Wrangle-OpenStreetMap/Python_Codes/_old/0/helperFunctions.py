def getList(file):
    with open(file,"r") as f:
        new_List = f.readlines()
        new_List = [item.strip('\n') for item in new_List]
    return new_List

def getDict(file):
    new_Dict = {}
    with open(file,"r") as f:
        for line in f:
            (k, v) = line.split(':')
            new_Dict[k] = v.strip()
    return new_Dict