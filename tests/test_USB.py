from Naked.toolshed.shell import execute_js, muterun_js
import sys

def run():

    # response = muterun_js("../src/scene.py", *args)
    # response = execute_js("../src/scene.js")
    cmd = "node ../src/scene.js 1"

    subprocess.run(cmd, shell = True )
    # if response.exitcode == 0:
    # if response:
    #     print("got here")
    # else:
    #     sys.stderr.write("erro")

if __name__ == "__main__":
    run()
