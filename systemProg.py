import pandas as pd





def readPandas(url):
    df=pd.read_table("Assembly.txt", sep='\t', names=['Label', 'Mnemonic', 'Operand'])
    df.fillna('_',inplace=True)
    return df


def Pass1(s):
    LOCCTR = 0
    i=1
    startAddress=0
    programLength=0
    st=s.iloc[0,1]

    if st=="START":
        intVal = s.iloc[0, 2]  #check if first statement is START
        LOCCTR = int(intVal,16)
        startAddress=LOCCTR
        print(LOCCTR)
    size=len(s)
    print(i)
    while (i!=size): #Remove Comments
        if s.iloc[i,0] =='.':
            s1=s.drop(i)
        i+=1
    print(s1)
    i=1                              #Set the index to the second row After removing all comments
    SYMTAB={'Label':[],'address':[]}
    SYMTAB['Label'].append(s1.iloc[0,0])    #Put Program Name & address
    SYMTAB['address'].append(format(int(s1.iloc[0,2],16),'06X'))
    OPTAB    = {'ADD': '18',
                'AND': '40',
                'COMP': '28',
                'DIV': '24',
                'J': '3C',
                'JEQ': '30',
                'JGT': '34',
                'JLT': '38',
                'JSUB': '48',
                'LDA': '00',
                'LDCH': '50',
                'LDL': '08',
                'LDX': '04',
                'MUL': '20',
                'OR': '44',
                'RD': 'D8',
                'RSUB': '4C',
                'STA': '0C',
                'STCH': '54',
                'STL': '14',
                'STSW': 'E8',
                'STX': '10',
                'SUB': '1C',
                'TD': 'E0',
                'TIX': '2C',
                'WD': 'DC'
                }
    size1=len(s1)
    while i != size1-1:

        if s1.iloc[i,0] != '_':                             #Check if there is a symbol in label field
            if SYMTAB['Label'].__contains__(s1.iloc[i,0]):  #Check that there is no duplicate in SYMTAB
                print("Duplicate symbol")
                raise Exception("Duplicate symbol found")

            else:
                SYMTAB['Label'].append(s1.iloc[i,0])
                SYMTAB['address'].append(format(LOCCTR,'06X'))
        if OPTAB.__contains__(str(s1.iloc[i,1])):                   #Check if mnemonic in OPTAB
            LOCCTR+=3
        elif s1.iloc[i,1] == 'WORD':                        #Check if WORD
            LOCCTR+=3
        elif s1.iloc[i,1] == 'RESW':                        #Check if RESW
            LOCCTR=LOCCTR+3*int(s1.iloc[i,2])
        elif s1.iloc[i,1] == 'RESB':                        #Check if RESB
            LOCCTR=LOCCTR+ int(s1.iloc[i,2])
        elif s1.iloc[i,1] == 'BYTE':                        #check if BYTE
            LOCCTR=LOCCTR+ len(s1.iloc[i,2])
        else:
            raise Exception("Invalid operation code")
            print(i)
        i+=1
    programLength=LOCCTR-startAddress
    dfSYMTAB=pd.DataFrame.from_dict(SYMTAB)                                     #change from dictionary to data frame
    print(dfSYMTAB)
    dfSYMTAB.to_csv("SYMTAB",sep='\t',header=None,index=None,mode='w')          #Write data frame into file
    return programLength,startAddress,OPTAB,dfSYMTAB,s1



def Pass2(programLength,startAddress,OPTAB,SYMTAB,AssemblyCode):
    label=SYMTAB['Label'].tolist()
    address=SYMTAB['address'].tolist()
    x=0
    i=1
    opcode=0
    operand=""
    symAdd=0
    add=0
    flag=0
    ascii=""
    bytereserved=0
    reserved=0
    recordstart=startAddress
    nextrecordstart=startAddress
    objectProgram=""
    currentObjectCode=""
    if AssemblyCode.iloc[0,1]=='START':
        recordstart = startAddress
        nextrecordstart = startAddress
    objectProgram=objectProgram+"H"+" "+AssemblyCode.iloc[0,0]+" "+format(recordstart,'06X')+" "+format(programLength,'06X')+"\n"
    size=len(AssemblyCode)
    while i != size-1:
        flag=0
        if (len(currentObjectCode)==60)|(len(currentObjectCode)+6)>60:
            if (len(currentObjectCode)+6)>60:
                nextrecordstart+=60-len(currentObjectCode)
            objectProgram=objectProgram+"T"+" "+format(recordstart,'06X')+" "+format((len(currentObjectCode)/2),'02X')+" "+currentObjectCode+"\n"
            recordstart=nextrecordstart
            currentObjectCode=""
        if OPTAB.__contains__(str(AssemblyCode.iloc[i,1])):
            opcode=int(OPTAB[AssemblyCode.iloc[i,1]],16)
            nextrecordstart+=3
            operand=AssemblyCode.iloc[i,2]
            if operand =="_":
                if AssemblyCode.iloc[i,1]=='RUSB':
                    add=0
                else:
                    raise Exception("Operand missing")
            else:
                if operand.__contains__(","):
                    x=32768 #0X8000
                else:
                    x=0
            if x!=0:
                operand=operand.replace(operand[len(operand)-1],"")
                operand=operand.replace(",","")

            symAdd=label.index(operand)
            add=x+int(address[symAdd],16)
            flag=1
            if flag!=1:
                raise Exception("Invalid symbol")
            currentObjectCode=currentObjectCode+" "+format(opcode,'02X')+format(add,'04X')
        elif AssemblyCode.iloc[i,1]=='WORD':
            nextrecordstart+=3
            currentObjectCode=currentObjectCode+" "+format(int(AssemblyCode.iloc[i,2],16),'06X')
        elif AssemblyCode.iloc[i,1]=='BYTE':
            operand=AssemblyCode.iloc[i,2]
            if operand.__contains__('X'):
                operand=operand.replace("X","")
                operand=operand.replace("'","")
                nextrecordstart+=1
                if len(currentObjectCode)+len(operand) >60:
                    objectProgram = objectProgram+ "T"+" " + format(recordstart, '06X')+" " + format((len(currentObjectCode) / 2), '02X')+" " + currentObjectCode + "\n"
                    recordstart = nextrecordstart
                    currentObjectCode = ""
                currentObjectCode=currentObjectCode+" "+operand
            elif operand.__contains__('C'):
                operand=operand.replace("C","")
                operand=operand.replace("'","")
                nextrecordstart+=len(operand)
                if len(currentObjectCode)+len(operand) >60:
                    objectProgram = objectProgram + "T"+" " + format(recordstart, '06X')+" " + format((len(currentObjectCode)/ 2), '02X')+" " + currentObjectCode + "\n"
                    recordstart = nextrecordstart
                    currentObjectCode = ""
                for a in operand:
                    ascii=ascii+ord(operand[a])
                currentObjectCode=currentObjectCode+" "+ascii
            else:
                nextrecordstart += 1

                if len(currentObjectCode) + 2 > 60:
                    objectProgram = objectProgram + "T"+" " + format(recordstart, '06X')+" " + format(int((len(currentObjectCode) / 2)),'02X')+" " + currentObjectCode + "\n"
                    recordstart = nextrecordstart
                    currentObjectCode = ""
                currentObjectCode=currentObjectCode+" "+format(int(operand,16),'02X')
        elif AssemblyCode.iloc[i,1]=='RESW' or AssemblyCode.iloc[i,1]=='RESB':
            while AssemblyCode.iloc[i,1]=='RESW' or AssemblyCode.iloc[i,1]=='RESB':
                if AssemblyCode.iloc[i,1]=='RESW':
                    reserved=int(AssemblyCode.iloc[i,2])
                    bytereserved+=reserved*3
                elif AssemblyCode.iloc[i,1]=='RESB':
                    reserved=int(AssemblyCode.iloc[i,2])
                    bytereserved+=reserved
                i+=1
            i-=1
            objectProgram = objectProgram+ "T"+" " + format(recordstart, '06X')+" " + format(int((len(currentObjectCode) / 2)),'02X')+" " + currentObjectCode + "\n"
            nextrecordstart=recordstart
            nextrecordstart+=(len(currentObjectCode)/2)+bytereserved
            recordstart=nextrecordstart
            currentObjectCode=""
        i+=1
    print(currentObjectCode)
    print(recordstart)
    objectProgram=objectProgram+"T"+format(int(recordstart),'06X')+format(int((len(currentObjectCode)/2)),'02X')+currentObjectCode+"\n"
    objectProgram=objectProgram+"E"+" "+format(startAddress,'06X')
    return objectProgram




df =readPandas('kk')
print(df)
programLength,startAddress,OPTAB,dfSYMTAB,AssemblyCode=Pass1(df)
print(dfSYMTAB.iloc[0,0])
objectProgram=Pass2(programLength,startAddress,OPTAB,dfSYMTAB,AssemblyCode)
print(objectProgram)
#make a programLength variable in pass1 function