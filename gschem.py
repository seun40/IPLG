#!/usr/bin/env python
import os,sys
import time
import random
from io import BytesIO
from struct import pack, unpack
import array, math
import glob
# local module
try:
    import nbt
except ImportError:
    # nbt not in search path. Let's see if it can be found in the parent folder
    extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
    if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
        raise
    sys.path.append(extrasearchpath)
from nbt.nbt import NBTFile, TAG_Short, TAG_Int, TAG_String, TAG_List, TAG_Byte, TAG_Byte_Array, TAG_Compound
"""'
# Example usage
from genetic import *
target = 371
p_count = 100
i_length = 6
i_min = 0
i_max = 100
p = population(p_count, i_length, i_min, i_max)
fitness_history = [grade(p, target),]
for i in xrange(100):
    p = evolve(p, target)
    fitness_history.append(grade(p, target))

for datum in fitness_history:
   print datum
methodology:
MCEdit(Minecraft World) -> NBTExplorer(.schematic) -> text2book(block array) -> source book
source book -> child book
child book -> MCEdit(.schematic) -> Minecraft World
nbtexplorer can export .schematic block array as text which is coverted to
a book(base91 string) representing a the 3D block array
The translation table is composed of the remaining characters as shown below.

0	A	0x41	 	13	N	0x4E	 	26	a	0x61	 	39	n	0x6E	 	52	0	0x30	 	65	%	0x25	 	78	>	0x3E
1	B	0x42	14	O	0x4F	27	b	0x62	40	o	0x6F	53	1	0x31	66	&	0x26	79	?	0x3F
2	C	0x43	15	P	0x50	28	c	0x63	41	p	0x70	54	2	0x32	67	(	0x28	80	@	0x40
3	D	0x44	16	Q	0x51	29	d	0x64	42	q	0x71	55	3	0x33	68	)	0x29	81	[	0x5B
4	E	0x45	17	R	0x52	30	e	0x65	43	r	0x72	56	4	0x34	69	*	0x2A	82	]	0x5D
5	F	0x46	18	S	0x53	31	f	0x66	44	s	0x73	57	5	0x35	70	+	0x2B	83	^	0x5E
6	G	0x47	19	T	0x54	32	g	0x67	45	t	0x74	58	6	0x36	71	,	0x2C	84	_	0x5F
7	H	0x48	20	U	0x55	33	h	0x68	46	u	0x75	59	7	0x37	72	.	0x2E	85	`	0x60
8	I	0x49	21	V	0x56	34	i	0x69	47	v	0x76	60	8	0x38	73	/	0x2F	86	{	0x7B
9	J	0x4A	22	W	0x57	35	j	0x6A	48	w	0x77	61	9	0x39	74	:	0x3A	87	|	0x7C
10	K	0x4B	23	X	0x58	36	k	0x6B	49	x	0x78	62	!	0x21	75	;	0x3B	88	}	0x7D
11	L	0x4C	24	Y	0x59	37	l	0x6C	50	y	0x79	63	#	0x23	76	<	0x3C	89	~	0x7E
12	M	0x4D	25	Z	0x5A	38	m	0x6D	51	z	0x7A	64	$	0x24	77	=	0x3D	90	"	0x22
cross over, cross over chunk by chunk
"""
index = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',24:'Y',25:'Z',26:'a',27:'b',28:'c',29:'d',30:'e',31:'f',32:'g',33:'h',34:'i',35:'j',36:'k',37:'l',38:'m',39:'n',40:'o',41:'p',42:'q',43:'r',44:'s',45:'t',46:'u',47:'v',48:'w',49:'x',50:'y',51:'z',52:'0',53:'1',54:'2',55:'3',56:'4',57:'5',58:'6',59:'7',60:'8',61:'9',62:'!',63:'#',64:'$',65:'%',66:'&',67:'(',68:')',69:'*',70:'+',71:',',72:'.',73:'/',74:':',75:';',76:'<',77:'=',78:'>',79:'?',80:'@',81:'[',82:']',83:'^',84:'_',85:'`',86:'{',87:'|',88:'}',89:'~',90:'"'}
iindex = {y:x for x,y in index.items()} #inverse index

class foo():
    id = 10

def access(filename):
    #get string from filename
    return list(open(filename,'r').read())

def deactv(string,name="child.tmp"):
    with open(name, 'w') as p:
        p.write(string)
    return name

def individual(length):
    'Create a member of the population.'
    return [index[random.choice(range(90))] for x in range(length) ]

def population(count=20, length=4194304,disk=False):
    """
    Create a number of individuals (i.e. a population).

    count: the number of individuals in the population
    length: the number of values per individual
    min: the minimum possible value in an individual's list of values
    max: the maximum possible value in an individual's list of values

    """
    c = []
    if disk:
        #disk
        x = []
        for r in range(count):
            print("Iv "+str(r))
            x.append(''.join(individual(length)))
        u = 0
        for _ in x:
            with open(str(u)+'.tmp', 'w') as p:
                p.write(_)
            c.append(str(u)+'.tmp')        
            u = u+1
        print(c)
    else:
        c = [individual(length) for x in range(count) ]
    return c

def artpop(count=20, length=4194304):
    """create artificial population, non random individuals"""
    return [[index[(x+1%90)]]*length for x in range(count)]

def fitness(individual, target=0,disk=False):
    """
    Determine the fitness of an individual. Higher is better.

    individual: the individual to evaluate
    target: the target number individuals are aiming for
    """
    #todo
    return random.randint(0, 15)

def grade(pop, disk=False,target=0):
    'Find average fitness for a population.'
    summed = sum([fitness(x, target, disk) for x in pop])
    return summed / (len(pop) * 1.0)

def evolve(pop, length=4194304, target=0, retain=0.25, random_select=0.05, mutate=0.01,disk=False):
    graded = [ (fitness(x, target,disk), x) for x in pop]
    graded = [ x[1] for x in sorted(graded)]
    retain_length = int(len(graded)*retain)
    parents = graded[:retain_length]
    # randomly add other individuals to
    # promote genetic diversity
    for individual in graded[retain_length:]:
        if random_select > random.random():
            parents.append(individual)
    # mutate some individuals
    for individual in parents:
        if mutate > random.random():
            if disk:
                oseds = access(individual)
            else:
                oseds = individual
            for x in range(int(length*0.01)):
                #mutate 1% of the positions of an individual
                pos_to_mutate = random.randint(0, len(oseds)-1)
                # this mutation is not ideal, because it
                # restricts the range of possible values,
                # but the function is unaware of the min/max
                # values used to create the individuals,
                oseds[pos_to_mutate] = index[random.choice(range(90))]
                #randint(min(individual), max(individual))
    # crossover parents to create children
    parents_length = len(parents)
    desired_length = len(pop) - parents_length
    children = []
    iuo = 0
    while len(children) < desired_length:
        male = random.randint(0, parents_length-1)
        female = random.randint(0, parents_length-1)
        if male != female:
            if disk:
                male = access(parents[male])
                female = access(parents[female])
            else:
                male = parents[male]
                female = parents[female]
            #chunk select: (x%128)<16 and (x%16384)<2048
            child = []
            print("C"+str(iuo)+",",end="",flush=True)
            for k in range(4194304):
                if ((k%128)%32)<16 and ((k%16384)%4096)<2048:
                    child.append(male[k])
                    #sys.stdout.write("m")
                elif ((k%128)%32)>=16 and ((k%16384)%4096)>=2048:
                    child.append(male[k])
                    #sys.stdout.write("m")
                else:
                    child.append(female[k])
                    #sys.stdout.write("f")
            #half = len(male) / 2
            #child = male[:half] + female[half:]
            if disk:
                child = deactv(''.join(child),str(iuo)+"child.tmp")
            children.append(child)
            iuo = iuo+1
    #print("\n")
    parents.extend(children)
    return parents

def _schema(h=256,l=128,w=128,blst=[0]*4194304):
    if len(blst) < 4194304:
        #pad
        blst = blst + [0]*(4194304-len(blst))
    elif len(blst) > 4194304:
        #truncate
        blst = blst[:4194304]
    result = NBTFile() #Blank NBT
    result.name = "Schematic"
    result.tags.extend([
        TAG_Short(name="Height", value=h),
        TAG_Short(name="Length", value=l),
        TAG_Short(name="Width", value=w),
        TAG_Byte_Array("Biomes",gbba([0]*16384,True)),
        TAG_Byte_Array("Blocks", gbba(blst,True)),
        TAG_Byte_Array("Data",gbba([0]*4194304,True)),
        TAG_String(name="Materials", value="Alpha"),
        TAG_List(type=foo(),name="Entities"),
        TAG_List(type=foo(),name="TileEntities"),
        TAG_List(type=foo(),name="TileTicks")
    ])
    return result


def gbba(blocksList, buffer=False):
    """Return a list of all blocks in this chunk."""
    if buffer:
        length = len(blocksList)
        return BytesIO(pack(">i", length)+gbba(blocksList))
    else:
        return array.array('B', blocksList).tostring()
#@profile
def main(auto=False,fold='firstrun',fake=True):
    gui = """
#########################################################
Intelligent Procedural Level Generation #2.00
using Minecraft, MCEdit, NBTExplorer
source: {}
cmd: select source - 0, generate schematic - 1, test schematic - 2, exit - 3
"""
    while True:
        if(auto):
            sourcename = glob.glob('books/*.source')[0]
            f = open(sourcename,'r')
            source = f.read()
            f.close()
            cmd = 1
        else:
            try:
                print(gui.format(sourcename))
            except:
                try:
                    sourcename = glob.glob('books/*.source')[0]
                    f = open(sourcename,'r')
                    source = f.read()
                    f.close()
                    continue
                except:
                    print('<SEED REQUIRED>')
                    print('add .source to book dir and')
                    input('press enter')
                    continue
            try:
                cmd = int(input('c: '))
            except:
                print("command must be integer")
                continue
        if cmd == 0:#select source
            directory = glob.glob('books/*.source')
            print(directory)
            wid = input('Select Source ID: ')
            try:
                sourcename = directory[int(wid)]
            except:
                continue
            handle = open(sourcename,'r')
            source = handle.read()
            handle.close()
        elif cmd == 1:#generate schematics
            if auto:
                name = fold
            else:
                name = input('Book Folder name:')
                try:
                    fake = int(input('Random - 0 or Solid - 1'))
                except:
                    fake = False
            if name == "":
                continue
            j = "schema/"+name+"/"
            k = "books/"+name+"/"
            if not os.path.exists(j):
                os.makedirs(j)
            if not os.path.exists(k):
                os.makedirs(k)
            if fake:
                p = artpop()
            else:
                p = population()
            fitness_history = [grade(p)]
            print("generation INTIAL")
            print(fitness_history[0])
            for i in range(100):
                print("generation "+str(i))
                p = evolve(p)
                r = grade(p)
                fitness_history.append(r)
                print(r)
            #for datum in fitness_history:
                #print(datum)
            #last p
            jkl = 0
            p = [(fitness(x), x) for x in p]
            p = [x[1] for x in sorted(p)]
            for _ in p:
                m = access(_)
                mpl = [iindex[x] for x in m]
                mps = ''.join(m)
                with open(k+str(jkl)+'.book', 'w') as a:
                    a.write(mps)
                mine = _schema(blst=mpl)
                mine.write_file(j+str(jkl)+'.schematic')
                jkl = jkl+1
            trash = glob.glob('*.tmp')
            for z in trash:
                os.remove(z)
            if auto:
                break
        elif cmd == 3:#exit
            break
        elif cmd == 2:#test schematic
            name = input('Schematic Name:')
            try:
                typ = input('Type? B - Blank, R - Random, L - Random Legal, S - Source\n: ').lower()
            except:
                typ ='b'
            if name == "":
                continue
            if typ == 'b':
                mine = _schema()
            elif typ == 'r':
                mine = _schema(blst=[iindex[_] for _ in [random.choice(range(197)) for _ in range(4194304)]])
            elif typ == 'l':
                mpl = [index[random.choice(range(90))] for _ in range(4194304)]
                mps = ''.join(mpl)
                with open('books/'+typ.upper()+name+".book", 'w') as _:
                    _.write(mps)
                mine = _schema(blst=[iindex[_] for _ in mpl])
            elif typ == 's':
                srce = open("books/"+name+".book", 'r')
                mine = _schema(blst=[iindex[_] for _ in list(srce.read())])
                srce.close()
            else:
                typ = 'b'
                mine = _schema()
            print(mine.pretty_tree())
            mine.write_file("schema/"+typ.upper()+name+".schematic")
        else:
            print("Command {} is not found".format(cmd))
    return 0


if __name__ == '__main__':
    """schmatic = _schema()
    print(schmatic.pretty_tree())
    schmatic.write_file("artificial2.schematic")"""
    if len(sys.argv) >= 2:
        try:
            sys.exit(main(True,sys.argv[1]))
        except:
            sys.exit(main(True))
    else:
        sys.exit(main())
