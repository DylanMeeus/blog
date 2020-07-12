import os

if __name__ == '__main__':
    os.system("sudo rm -rf " + os.environ["GHBLOG"] + "*")
    os.system("sudo cp -r public/* " + os.environ["GHBLOG"])
    os.system("cd " + os.environ["GHBLOG"])
    os.system("git add .")
    os.system("git commit -m \"publish blog\"")
    os.system("cd -")
