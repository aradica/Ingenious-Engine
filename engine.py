import tkinter as tk
import threading
import time


class MetaBall:
    def __init__(self, canvas, mass, radius, color, x, y, vx, vy):
        # Static info (hopefully...)
        self.canvas = canvas
        self.id = None

        self.mass = mass
        self.radius = radius

        self.color = color

        # These should change
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        # These are used to determine the change
        self.fx = 0
        self.fy = 0

    def setFx(self, amount):
        self.fx = amount

    def setFy(self, amount):
        self.fy = amount

    def move(self, timestep):
        ax = self.fx / self.mass
        vx = ax * timestep
        sx = (vx * timestep) / 2

        ay = self.fy / self.mass
        vy = ay * timestep
        sy = (vy * timestep) / 2

        self.x += self.vx * timestep + sx
        self.y += self.vy * timestep + sy

        self.vx += vx
        self.vy += vy

    def erase(self):
        self.canvas.delete(self.id)

    def draw(self):
        x, y, r = self.x, self.y, self.radius
        self.id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.color)

# TODO: Separate window for telemetry


class Game:
    timestep = 0.01
    framestep = 0.05
    logstep = 5

    def __init__(self, canvas, objects=[], bindings={}, log=True):
        self.canvas = canvas
        # Set of objects
        self.objects = objects

        self.bindings = bindings

        # Info
        self.engineFrame = 0
        self.engineFramesMissed = 0

        self.viewFrame = 0
        self.viewFramesMissed = 0

        self.logger = threading.Thread(target=self._logger)
        self.logger.daemon = True
        if log:
            self.logger.start()

    def _logger(self):
        print("* Engine step:", self.timestep)
        print("* Frame step:", self.framestep)
        print("* Telemetry displayed every", self.logstep, "seconds")
        next_call = time.time()
        while True:
            print("+----------------------------+")
            print("Engine frame:", self.engineFrame)
            print("Engine frames missed:", self.engineFramesMissed)
            print("View frame:", self.viewFrame)
            print("View frames missed:", self.viewFramesMissed)
            print("+----------------------------+")
            print()
            next_call += self.logstep
            time.sleep(next_call - time.time())

    def eventHandler(self, event):
        if self.logger.is_alive():
            print(event.type, event.char)

        if event.char in self.bindings:
            response = self.bindings[event.char.lower()][str(event.type)]
            response()

    def detectCollisions(self):
        pass

    def solveCollisions(self):
        # collisions = self.detectCollisions
        # TODO
        pass

    def _startEngine(self):
        next_call = time.time()
        while True:
            # Here we go!
            self.engineFrame += 1

            for obj in self.objects:
                obj.move(self.timestep)
                # TODO:
                # self.solveCollisions()

            # Calculate when to do the next iteration
            next_call += self.timestep
            rest = next_call + self.timestep - time.time()

            # 100% time, hopefully
            if rest > 0:
                time.sleep(rest)
            else:
                # Well f**k!
                self.engineFramesMissed += 1

    def startEngine(self):
        thread = threading.Thread(target=self._startEngine)
        thread.daemon = True
        thread.start()

    def _startStreaming(self):
        next_call = time.time()
        while True:
            self.viewFrame += 1
            for obj in self.objects:
                obj.erase()
                obj.draw()
            next_call += self.framestep
            rest = next_call + self.framestep - time.time()

            if rest > 0:
                time.sleep(rest)

            else:
                # Even greater f**k!!!
                self.viewFramesMissed += 1

    def startStreaming(self):
        thread = threading.Thread(target=self._startStreaming)
        thread.daemon = True
        thread.start()

    def run(self):
        self.startEngine()
        self.startStreaming()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    root.resizable(False, False)
    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill="both", expand=True)
    # canvas, mass, radius, color, x, y, vx, vy
    ball = MetaBall(canvas, 1, 15, "blue", 50, 50, 0, 0)

    myBindings = {
        "w": {
            "KeyPress": lambda: ball.setFy(-5),
            "KeyRelease": lambda: ball.setFy(0),
        },
        "s": {
            "KeyPress": lambda: ball.setFy(5),
            "KeyRelease": lambda: ball.setFy(0)
        },
        "a": {
            "KeyPress": lambda: ball.setFx(-5),
            "KeyRelease": lambda: ball.setFx(0)
        },
        "d": {
            "KeyPress": lambda: ball.setFx(5),
            "KeyRelease": lambda: ball.setFx(0)
        },
        "e": lambda: print("* bindings active")
    }

    game = Game(canvas, [ball], myBindings)
    root.bind("<Key>", game.eventHandler)
    root.bind("<KeyRelease>", game.eventHandler)
    game.run()
    root.mainloop()
