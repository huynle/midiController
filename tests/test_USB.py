from Naked.toolshed.shell import execute_js, muterun_js

def run():

    # response = muterun_js("../src/scene.py", *args)
    response = execute_js("../src/scene.py")

    if response.exitcode == 0:
        print(response.stdout)
    else:
        sys.stderr.write(response.stderr)

if __name__ == "__main__":
    run()
