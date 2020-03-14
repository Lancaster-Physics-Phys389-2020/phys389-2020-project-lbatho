import sys
import shlex

from Common import *
from Particles import *
from Fields import *


def plot(args):
    try:
        x = tracked[args[1]]
        y = tracked[args[2]]
        plt.plot(x, y)
        plt.xlabel(args[1])
        plt.ylabel(args[2])
        plt.show()
    except IndexError:
        log("Invalid syntax. Should be of form:")
        log("plot 'x column' 'y column'")

def ex(args):
    sys.exit(0)

def dump(args):
    if args[1] == 'misc':
        df = misc
    elif args[1] == 'env':
        df = env
    elif args[1] == 'tracked':
        df = tracked
    else:
        log('Invalid data selection.')
        return
    if args[2] == 'csv':
        fname = name + '_' + args[1] + '.csv'
        df.to_csv(fname)
        log('Dumped as ' + fname)
    elif args[2] == 'pickle':
        fname = name + '_' + args[1] + '.pickle'
        with open(fname, 'wb') as f:
            pickle.dump(df, f)
        log('Dumped as ' + fname)
    else:
        log("Invalid file format. 'csv' or 'pickle' are supported only.")

def printcols(args):
    if len(args) == 1:
        print(list(tracked))
    elif args[1] == 'all':
        log(tracked)
    else:
        dic = {}
        for i in args:
            if i == 'printcols':
                continue
            try:
                dic.update({i: tracked[i]})
            except KeyError:
                log('Invalid column: ' + i)
        log(DataFrame(dic))

def dumpcols(args):
    if args[1] == 'all':
        dump(['dump', 'tracked', args[2]])
    else:
        dic = {}
        for i in args:
            if i == 'printcols':
                continue
            elif i == 'csv' or i == 'pickle':
                break
            try:
                dic.update({i: tracked[i]})
            except KeyError:
                log('Invalid column: ' + i)
        if i == 'csv':
            fname = name + '_trim.csv'
            DataFrame(dic).to_csv(fname)
            log('Dumped as ' + fname)
        elif i == 'pickle':
            fname = name + '_trim.pickle'
            with open(fname, 'wb') as f:
                pickle.dump(DataFrame(dic), f)
            log('Dumped as ' + fname)

def newcol(args):
    if len(args) != 2:
        raise IndexError
    dic = {}
    j = 0
    for i in list(tracked):
        dic.update({'a' + str(j): i})
        j += 1
    log('Column coefficients: ' + str(dic))
    func = input('    f: ')
    for k, v in dic.items():
        func = func.replace(k, "tracked['" + v + "'][i]")
    lis = []
    for i in range(len(tracked)):
        lis.append(eval(func))
    tracked[args[1]] = lis
    log('Succesfully added ' + args[1])

def hlp(args):
    log('plot <x> <y>                          - Plot given colums as x and y')
    log('printcols <columns>                   - Print given columns to screen')
    log('dump <misc/env/tracked> <csv/pickle>  - Dump misc, environment or tracked data to csv or DataFrame pickle')
    log('dumpcols <columns> <csv/pickle>       - Dump given columns to csv or DataFrame pickle')
    log('newcol <column_name>                  - Create new column, then populate with function of other column data')
    log('exit                                  - Quit program')

coms = {'exit': ex, 'plot': plot, 'dump': dump, 'printcols': printcols, 'dumpcols': dumpcols, 'newcol': newcol,
        'help': hlp}

inf = 'CyclotronSimulation_2020-03-14_00-03-06.pickle'# sys.argv[1]
name = inf.split('.')[0]

print('Simulation Analysis')
print('Logging to', log.fname)
log('Loading SimLog "' + inf + '"...', endLine = False)

with open(inf, 'rb') as f:
    data:SimLog = pickle.load(f)
env = data.getEnvData()
misc = data.getMiscData()
tracked = data.getTrackedData()
log('done')

log('== Misc Data ==')
for k, v in misc.items():
    log(str(k) + ' : ' + str(v))
log()
log('== Environment ==')
for k, v in env.items():
    log(str(k) + ' : ' + str(v))
log()
log('== Tracked ==')
log(list(tracked))
log()

while True:
    inp = input('> ')
    log.write(inp)
    c = shlex.split(inp)
    try:
        com = coms.get(c[0].lower())
        com(c)
    except TypeError or ValueError:
        log('Malformed comand.')