import os

if __name__ == '__main__':
    blogloc = os.environ["GHBLOG"]
    os.system("hugo")
    os.system("sudo rm -rf " + blogloc + "*")
    os.system("sudo cp -r public/* " + blogloc)
    os.system("cd " + os.environ["GHBLOG"])
    os.system("git add .")
    os.system("git commit -m \"publish blog\"")
    os.system("git push")
    os.system("cd -")
