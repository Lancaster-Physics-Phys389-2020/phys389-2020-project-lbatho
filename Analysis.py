import sys
import shlex
from math import sqrt

from Common import *
from Particles import *
from Fields import *

class AnalysisHandler:

    @classmethod
    def load(cls, inputFile: str) -> (DataFrame, DataFrame, DataFrame):
        with open(inputFile, 'rb') as f:
            data: SimLog = pickle.load(f)
        misc = data.getMiscData()
        env = data.getEnvData()
        tracked = data.getTrackedData()
        return misc, env, tracked

    @classmethod
    def dump(cls, df: DataFrame, fType: str, name: str) -> str:
        if fType == 'csv':
            fname = name + '.csv'
            df.to_csv(fname)
        elif fType == 'pickle':
            fname = name + '.pickle'
            with open(fname, 'wb') as f:
                pickle.dump(df, f)
        else:
            raise TypeError
        return fname

    def __init__(self, inputFile: str):
        self.name = inputFile.split('.')[0]
        self.misc, self.env, self.tracked = self.load(inputFile)

    def plot(self, x, y):
        plt.plot(self.tracked[x], self.tracked[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.show()

    def dumpcols(self, fType: str, cols: List[str]):
        dic = {}
        for i in cols:
            dic.update({i: self.tracked[i]})
        out = self.dump(DataFrame(dic), fType, self.name + '_trim')
        return out

    def newcol(self, name: str, func):
        lis = []
        if isinstance(func, str):
            for i in range(len(self.tracked)):
                lis.append(eval(func))
        else:
            for i in range(len(self.tracked)):
                lis.append(func(self.tracked, i))
        self.tracked[name] = lis

class AnalysisShell:

    def __init__(self, inputFile: str):
        self.an = None
        self.inputFile = inputFile
        self.name = inputFile.split('.')[0]
        self.coms = {'exit': self.ex, 'plot': self.plot, 'dump': self.dump,
                     'printcols': self.printcols, 'dumpcols': self.dumpcols,
                     'newcol': self.newcol, 'help': self.hlp}

    def plot(self, args):
        try:
            self.an.plot(args[1], args[2])
        except IndexError:
            log("Invalid syntax. Should be of form:")
            log("plot 'x column' 'y column'")

    def ex(self, args):
        sys.exit(0)

    def dump(self, args):
        if args[1] == 'misc':
            df = self.an.misc
        elif args[1] == 'env':
            df = self.an.env
        elif args[1] == 'tracked':
            df = self.an.tracked
        else:
            log('Invalid data selection.')
            return
        try:
            out = AnalysisHandler.dump(df, args[2], self.name + '_' + args[1])
            log('Dumped as ' + out)
        except TypeError:
            log("Invalid file format. 'csv' or 'pickle' are supported only.")

    def printcols(self, args):
        if len(args) == 1:
            print(list(self.an.tracked))
        elif args[1] == 'all':
            log(str(self.an.tracked))
        else:
            dic = {}
            for i in args:
                if i == 'printcols':
                    continue
                try:
                    dic.update({i: self.an.tracked[i]})
                except KeyError:
                    log('Invalid column: ' + i)
            log(DataFrame(dic))

    def dumpcols(self, args):
        if args[1] == 'all':
            try:
                out = AnalysisHandler.dump(self.an.tracked, args[2], self.name + '_trim')
                log('Dumped as ' + out)
            except TypeError:
                log("Invalid file format. 'csv' or 'pickle' are supported only.")
        else:
            cols = []
            j = ''
            for i in args:
                if i == 'dumpcols':
                    continue
                elif i == 'csv' or i == 'pickle':
                    j = i
                    break
                else:
                    cols.append(i)
            try:
                out = self.an.dumpcols(j, cols)
            except KeyError:
                log('Invalid column selection.')

    def newcol(self, args):
        if len(args) != 2:
            log('No name provided.')
            return
        dic = {}
        j = 0
        for i in list(self.an.tracked):
            dic.update({'a' + str(j): i})
            j += 1
        log('Column coefficients: ' + str(dic))
        func = input('    f: ')
        for k, v in dic.items():
            func = func.replace(k, "self.tracked['" + v + "'][i]")
        self.an.newcol(args[1], func)
        log('Succesfully added ' + args[1])

    def hlp(self, args):
        log('plot <x> <y>                          - Plot given colums as x and y')
        log('printcols <columns>                   - Print given columns to screen')
        log('dump <misc/env/tracked> <csv/pickle>  - Dump misc, environment or tracked data to csv or DataFrame pickle')
        log('dumpcols <columns> <csv/pickle>       - Dump given columns to csv or DataFrame pickle')
        log(
            'newcol <column_name>                  - Create new column, then populate with function of other column data')
        log('exit                                  - Quit program')

    def start(self):
        print('Simulation Analysis')
        print('Logging to', log.fname)
        log('Loading SimLog "' + self.inputFile + '"...', endLine = False)
        self.an = AnalysisHandler(self.inputFile)
        log('done')
        log()
        log('== Misc Data ==')
        for k, v in self.an.misc.items():
            log(str(k) + ' : ' + str(v))
        log()
        log('== Environment ==')
        for k, v in self.an.env.items():
            log(str(k) + ' : ' + str(v))
        log()
        log('== Tracked ==')
        log(list(self.an.tracked))
        log()

        while True:
            inp = input('> ')
            log.write(inp)
            try:
                c = shlex.split(inp)
                com = self.coms.get(c[0].lower())
                com(c)
            except TypeError or ValueError:
                log('Malformed comand.')
            except IndexError:
                log('Not enough arguments.')
