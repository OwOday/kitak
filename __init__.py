from binaryninja import *
from binaryninja.plugin import PluginCommand
        
def test(bv:binaryninja.BinaryView, function: binaryninja.function.Function):
    for i in range(function.lowest_address, function.highest_address):
        refs = bv.get_code_refs_from(i,function)
        for j in refs:
            print(hex(j))        


def get_data_references(function: binaryninja.function.Function, data_references: dict, bv: binaryninja.BinaryView):
    for i in range(function.lowest_address, function.highest_address):
        refs = bv.get_code_refs_from(i,function)
        for j in refs:
            data_references[j]=bv.read(j,4)
            print(data_references[j])
                # nvalue = data_references[j]
                # if nvalue < bv.end and nvalue >= bv.start:
                #     if bv.is_offset_readable(nvalue) and not bv.is_offset_executable(nvalue):
                #         data_references[nvalue]=bv.read(nvalue,4) #TODO this hardcoded 4 will break anything but addresses/ints (strings for example)
                                      
def recursive_functions(function:binaryninja.function.Function,functions:dict,vars:dict,bv:binaryninja.BinaryView):
    called=function.callees
    #get_data_references(function,vars,bv)
    i: binaryninja.function.Function
    for i in called:
        if i.lowest_address not in functions:
            functions[i.lowest_address]=i
            recursive_functions(i,functions,vars,bv)

def kitak(bv:binaryninja.BinaryView ,function: binaryninja.function.Function):
    functions:dict [int,binaryninja.function.Function] ={}
    variables={}
    functions[function.lowest_address]=function
    recursive_functions(function,functions,variables,bv) #populate recursively
    base=bv.mapped_address_ranges[0].start
    size=bv.mapped_address_ranges[0].end - base
    output=[0]*size
    bytes_bv = bv.read(base,size)
    for i,j in enumerate(bytes_bv):
        output[i]=j
    for i in bv.functions:
        #do badness
        if i.lowest_address not in functions:
          broken = False
          adr = i.lowest_address
          while not broken:
              if adr in functions or adr >= i.highest_address:
                    broken = True
              else:
                  output[adr-base]=0
              adr+=1
    # for i in functions:
    #     #print(base,size,i,functions[i].highest_address,functions[i].lowest_address)
    #     bytes_read=bv.read(i,functions[i].highest_address - i + 1)
    #     for j,k in enumerate(bytes_read):
    #         output[i-base+j]=k
    # print(variables)
    # for i in variables:
    #     if size+base > i > base:
    #         for j,k in enumerate(bv.read(i,4)):
    #             output[i-base+j]=k
    #             print(i-base+j,k)
    #             print(hex(i+j),hex(k))
    # #fuck it, just kludge the shit
    # for i in range(size):
    #     if not bv.is_offset_executable(i+base):
    #         output[i]=bv.read(i+base,1)[0]
            
    with open("kitak.txt","wb") as f:
        for i in output:
            f.write(i.to_bytes(1,"little"))
    show_message_box("Kitak",f"Output to ~/kitak.txt\nMake a function in binja in the newly loaded file at the offset of the function you were in during the run enable full analysis of that function then do full analysis\nDont forget to load it with the same offset\nThis many functions: {len(functions)}\nThis many references: {len(variables)}", MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.InformationIcon)

PluginCommand.register_for_function("kitak", "Basically does something", kitak)
PluginCommand.register_for_function("kitak_test", "Basically does something", test)