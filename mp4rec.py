import os
from threading import Thread

mp4start = b'\x66\x74\x79\x70'


def creatdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class fileobg:

    def __init__(self, orgpath, start=0, save_path=None, end=0, data=None):
        self.start = start
        self.endstr = "mp4"
        self.save_path = f"./{self.endstr}/"
        if save_path is not None:
            self.save_path = save_path

        self.in_path = orgpath
        self.in_file = None
        self.size = 0
        self.out_file = None
        self.read_buffer = 1024 * 1024
        self.tmpdata = None

    def open_in_file(self):
        try:
            self.in_file = open(self.in_path, "rb")
        except Exception as e:
            print(e, "could not open ", self.in_file)
            self.in_file = None

    def open_out_file(self, name):
        try:
            path = self.save_path
            creatdir(path)
            self.out_file = open(path + f"{name}.{self.endstr}", "wb")

        except Exception as e:
            print(e, "could not open ", self.out_file)
            self.out_file = None

    def get_size(self):
        self.open_in_file()
        if self.in_file:

            npos = self.start
            while True:
                res = self.get_chunk_at(npos, 4)
                if res > 0:
                    npos = res + npos
                else:
                    break
            self.size = npos - self.start

            print("size is : ", int(self.size / 2 ** 20), " MB")
        return self.size

    def save(self, name):
        self.get_size()
        return self.getdata_fromfile(name)

    def get_chunk_at(self, pos, length=32):
        try:
            self.seek_to_pos(pos)
            chunk = self.in_file.read(length)
            data = int.from_bytes(chunk, "big")
            return data
        except Exception as e:
            # print(e,"failled to read at pos :",pos)
            return 0

    def fileread(self, file):
        try:
            chunk = file.read(self.read_buffer)
            return chunk
        except Exception as e:
            print(e, file.tell())

            return b''

    def seek_to_pos(self, pos):
        try:
            self.in_file.seek(pos)
        except Exception as e:
            m = self.in_file.tell()
            self.in_file.read(pos - m)
            # print(e, "failed to seek pos:", pos)

    def getdata_fromfile(self, name):
        try:
            self.open_out_file(name)
            self.in_file.seek(self.start)
            saved = 0
            while saved < self.size:

                data = self.fileread(self.in_file)
                if len(data) > 0:
                    saved += self.read_buffer
                    self.sava_data(data, name)
                else:
                    break

            return True
        except Exception as e:
            print(e)
            return False

    def sava_data(self, data, name):
        try:
            path = self.save_path
            creatdir(path)
            with open(path + f"{name}.{self.endstr}", "ab") as out_file:
                out_file.write(data)
            return True
        except Exception as e:
            print(e, name)
            return False

    def get_tmp_data(self):
        size = self.get_size()
        if size > 1024 * 1024 * 100:
            size = 1024 * 1024 * 100
        try:
            self.open_in_file()
            if self.in_file and not self.tmpdata:
                self.seek_to_pos(self.start)
                saved = 0
                tmpdata = b''
                while saved < size:
                    data = self.fileread(self.in_file)
                    if len(data) > 0:
                        tmpdata += data
                        saved += self.read_buffer
                    else:
                        break

            return tmpdata

        except Exception as e:
            print(e)


class fileReco:

    def __init__(self, path="", buffer=1024 * 1024, startpos=0):
        self.path = path
        self.buffer = buffer  # buffer in bytes
        self.filecount = 500000
        self.switch = True
        self.searching = False
        self.results = []
        self.resultspos = []
        self.totalsearched = 0
        self.startpos = startpos

    def set_path(self, path):
        self.path = f"\\\\.\\{path}:"

    def get_result(self):
        return self.results.copy()

    def findin(self, chunk, start, filepos, chunkpos=0):
        if filepos < 0:
            filepos = 0
        startindex = chunk[chunkpos:].find(start)
        if startindex > 0:
            realstart = filepos + startindex + chunkpos - 4
            newfile = fileobg(self.path, realstart)
            self.results.append(newfile)
            self.resultspos.append(realstart)
            return realstart
        else:
            return 0

    def getdata(self, file, chunk=None):
        try:
            newdata = file.read(self.buffer)

            self.totalsearched += self.buffer
            if chunk is not None:
                return chunk + newdata
            else:
                return newdata
        except Exception as e:
            print(e, "  ", self.totalsearched)
            self.totalsearched += self.buffer
            self.seek(file)
            return self.getdata(file, chunk)

    def seek(self, file, newpos=None):
        try:
            if newpos:
                self.totalsearched = newpos
                file.seek(newpos)
            else:
                self.totalsearched += self.buffer
                file.seek(self.totalsearched)

        except Exception as e:
            print(e, "  ", self.totalsearched)

    def startthread(self):
        Thread(target=self.start).start()

    def start(self):
        self.searching = True
        counter = 0
        print("started")
        try:
            with open(self.path, "rb") as in_file:
                if self.startpos:
                    self.seek(in_file, self.startpos)
                self.switch = True
                chunk = self.getdata(in_file)
                while self.switch and len(chunk) > 0:
                    filepos = in_file.tell() - self.buffer
                    pos = self.findin(chunk, mp4start, filepos)
                    if pos > 0:
                        print('Found mp4 at location: start ' + str(pos), "total found: ", counter)
                        if counter == self.filecount:
                            self.switch = False
                        counter += 1
                    chunk = self.getdata(in_file)
        except Exception as e:

            print(e, "failed to read the drive")

        self.searching = False
        print("finished")

    def save_all(self):

        for i, mp4 in enumerate(self.results):
            mp4.save(mp4.start)

    def saveresultspos(self, name):

        file = open(f"{name}.txt", "w")
        buffer = ""
        for item in self.resultspos:
            buffer = f"{buffer}!!!{item}"
        file.write(buffer)

    def stop(self):
        self.switch = False




