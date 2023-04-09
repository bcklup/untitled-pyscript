""" Main Python script for X system """


def main():
    """ Main program loop """
    print('test')


def shred(toggle):
    """ Shred Motor - 10s """
    if (toggle):
        print('Shredder enabled')
    else:
        print('Shredder disabled')


def stir(toggle):
    """ Stir """
    if (toggle):
        print('Stirrer motor enabled')
    else:
        print('Stirrer motor disabled')


def heat_filament(toggle):
    """ Heat Filament """
    if (toggle):
        print('Filament heater enabled')
    else:
        print('Filament heater disabled')


def solenoid(toggle):
    """ Activate solednoid valve """
    if (toggle):
        print('Solenoid opened')
    else:
        print('Solenoid closed')


print("Initial program execution\n---------------------------")
main()
