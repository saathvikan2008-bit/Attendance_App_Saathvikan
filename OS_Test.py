import os

cwd = (os.getcwd())

print(type(cwd))
print(os.listdir(cwd+"/RegisteredFaces"))

def initcheck():
    dir_list = os.listdir(cwd)
    print(dir_list)
    if "Records" not in dir_list:
        print("Records folder not Present, creating records folder")
        os.mkdir(cwd+"/Records")
    if "RegisteredFaces" not in dir_list:
        print("RegisteredFaces folder not present, creating directory")
        os.mkdir(cwd+'/RegisteredFaces')

dirname = os.path.dirname(os.path.realpath(__file__))
print(dirname)