import psutil


class HardDrives:

    def __init__(self):
        self.driver_list = psutil.disk_partitions()

    def get_available_list(self):
        list=[]
        for driver in self.driver_list:
            driverdict = {"name": driver.device.split(":\\")[0]}
            driverdict["Path"] = driver.device
            info = psutil.disk_usage(driver.device)
            driverdict["Total"] = round(info.total /2**30,2)
            driverdict["Used"] = round(info.used /2**30,2)
            driverdict["Free"] = round(info.free /2**30,2)
            list.append(driverdict)
        return list

    def reload(self):
        self.driver_list = psutil.disk_partitions()


if __name__ == '__main__':
    test = HardDrives()
    print(test.get_available_list())

    pass