from gpiozero import Button

switches = {
    'x_home': Button(17, pull_up=True),
    'x_elev1_button5': Button(18, pull_up=True),
    'x_elev2_button5': Button(23, pull_up=True),
    'x_call': Button(4, pull_up=True),
    'y_home': Button(5, pull_up=True),
    'y_call': Button(6, pull_up=True),
    'y_elev1_button5': Button(13, pull_up=True),
    'y_elev2_button5': Button(19, pull_up=True)
}

while True:
    for name, switch in switches.items():
        if switch.is_pressed:
            print(f"{name} pressed!")
    time.sleep(0.1)