import pandas
import time
from svviz import app

def run():
    commands = ["svviz demo 1 -a --no-web",
                "svviz demo 2 -a --no-web",
                "svviz demo 2 -a --no-web --auto-export",
                "svviz demo 3 -a --no-web"]
    times = []

    for command in commands:
        t0 = time.time()
        app.run(command.split(" "))
        times.append(time.time() - t0)

    print(pandas.DataFrame({"command":commands, "time (s)":times}))

    return (True, "")

if __name__ == '__main__':
    run()