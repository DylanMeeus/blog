import os

if __name__ == '__main__':
    blogloc = os.environ["GHBLOG"]
    if blogloc == "":
        print("invalid blog location")
        os.exit(1)

    currentloc = os.curdir
    os.system("hugo")
    os.system("sudo rm -rf " + blogloc + "*")
    os.system("sudo cp -r public/* " + blogloc)

    # nav to blog
    os.chdir(blogloc)

    os.system("git add .")
    os.system("git commit -m \"publish blog\"")
    os.system("git push")

    # back to previous
    os.chdir(currentloc)

