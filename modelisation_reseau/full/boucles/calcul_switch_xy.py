StationA = {"x":-29.443704481157962,"y":51.39560969429322}
StationB = {"x":-128.91874519860292,"y":47.69012367832095}

nbSwitch = 2

if(nbSwitch==2):
    x1 = (StationA.get("x") + StationB.get("x"))/2 - 5
    y1 = (StationB.get("y") + StationA.get("y"))/2 - 5
    x2 = (StationA.get("x") + StationB.get("x"))/2 + 5
    y2 = (StationB.get("y") + StationA.get("y"))/2 + 5
    print("Switch 1 : \"x\":",x1,",\"y\":",y1)
    print("Switch 2 : \"x\":",x2,",\"y\":",y2)

if(nbSwitch==4):
    x1 = (StationA.get("x") + StationB.get("x"))/2 - 7
    y1 = (StationB.get("y") + StationA.get("y"))/2 - 7
    x2 = (StationA.get("x") + StationB.get("x"))/2 - 3
    y2 = (StationB.get("y") + StationA.get("y"))/2 - 3
    x3 = (StationA.get("x") + StationB.get("x"))/2 + 3
    y3 = (StationB.get("y") + StationA.get("y"))/2 + 3
    x4 = (StationA.get("x") + StationB.get("x"))/2 + 7
    y4 = (StationB.get("y") + StationA.get("y"))/2 + 7
    print("Switch 1 : \"x\":",x1,",\"y\":",y1)
    print("Switch 2 : \"x\":",x2,",\"y\":",y2)
    print("Switch 3 : \"x\":",x3,",\"y\":",y3)
    print("Switch 2 : \"x\":",x4,",\"y\":",y4)


