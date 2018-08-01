import pyperclip

while True:
    argus = raw_input("input arguments:")
    ridestr = ""
    rideargus = ""
    keys = argus.split("|")
    for key in keys:
        if key.strip() != "":
            ridestr += "${%s}\t" % key.strip()
            rideargus += "${%s}|" % key.strip()
    pyperclip.copy(ridestr)

    print "\nride argus: %s\n" % rideargus[:-1]


