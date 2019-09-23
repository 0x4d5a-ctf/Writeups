from util import *
import traceback
import inspect
import struct
import math
import numpy as np
import sys

class Stackframe:
    def __init__(self):
        self.functionStart = 0x00
        self.returnAddr = 0x00

class StringBuffer:
    def __init__(self):
        self.length = 0x00
        self.selectionStart = 0x00
        self.selectionLength = 0x00
        self.data = ""

    def setData(self, data):
        self.length = len(data)
        self.data = data

class Emulator:
    def __init__(self, thecode):
        self.registers = {}
        self.registers["A"] = 0x00
        self.registers["X"] = 0x00
        self.registers["MA"] = [0,0,0]
        self.registers["MB"] = [0,0,0]
        self.registers["MC"] = [0,0,0]
        self.registers["S"] = 0x00 # Status
        self.registers["FS"] = "" # Field seperator


        for i in range(0, 128):
            self.registers["R%d" % i] = 0x00
        
        for i in range(1, 9):
            self.registers["T%d" % i] = 0x00

        self.registers["sb"] = StringBuffer()
        self.registers["pc"] = 0x01
        self.code = thecode
        self.stackframe = []
        for i in range(0, 10):
            self.stackframe.append(Stackframe())
        self.currentStackFrame = 0x00

        self.userdefinedfunctions = {} # Id and offset
        self.parseUserDefinedFunctions()

        self.isRunning = False
        self.debug = False
        self.instructionCounter = 0x00
    
    def parseUserDefinedFunctions(self):
        functionCounter = 0x00
        i = 0x00
        while (True):
            currentLen = self.code[i]
            retIns = self.code[i + currentLen]
            if (retIns == 0x80):
                self.userdefinedfunctions[functionCounter] = i
                i = i + currentLen + 1
                functionCounter += 1
            elif (retIns == 0x00):
                i += 1
                if (i >= len(self.code)):
                    break
            else:
                break

    def debugOutput(self, format, *options):
        if (self.debug):
            print("%04x: %s [%s] %s" % (self.registers["pc"], "--"*self.currentStackFrame + "->", inspect.stack()[1][3], (format % (options))))

    def dumpCode(self, filename):
        open(filename, "wb").write(bytes(self.code))


    def getRRegister(self, offset):
        return self.registers["R%d" % offset]

    def setRRegister(self, offset, value):
        self.registers["R%d" % offset] = value

    def setValueInARegister(self, value):
        self.setRRegister(self.registers["A"], value)
        
    def getValueInARegister(self):
        return self.getRRegister(self.registers["A"])

    def setValueInXRegister(self, value):
        self.setRRegister(self.registers["X"], value)
        
    def getValueInXRegister(self):
        return self.getRRegister(self.registers["X"])

    def eepromSlotToHex(self, slot):
        slotAddr = slot*4
        return struct.unpack("<I", bytes(self.code[slotAddr:slotAddr+4]))[0]

    def hexToEepromSlot(self, slot, value):
        slotAddr = slot*4
        packedValue = struct.pack("<I", value)
        counter = 0
        for i in packedValue:
            self.code[slotAddr+counter] = i
            counter +=1

    def unpackCode(self, code):
        return struct.unpack(">I", bytes(code))[0]

    def pack(self, code):
        return struct.unpack(">I", bytes(code))[0]

    def run(self):
        self.isRunning = True
        while (self.isRunning):
            self.registers["pc"] = self.registers["pc"] & 0x3ff
            currentOpcodes = self.code[self.registers["pc"]:]
            self.processOpcode(currentOpcodes)
            self.instructionCounter+=1

        if (self.debug):
            print("[+] Number of Instructions executed: %d" % self.instructionCounter)


    def processOpcode(self,opcode):
        currentOpcode = getOpcodeByByte(opcode[0])
        
        try:
            method = getattr(self, currentOpcode[0])
            method(opcode) # Includes the opcode the PC is currently at
        except Exception as e:
            traceback.print_exc()
            exit(0)
        pass

    def COPY(self, nextOpcodes):
        self.setRRegister(nextOpcodes[2], self.getRRegister(nextOpcodes[1]))
        self.registers["pc"] += 3

        self.debugOutput(" %d, %d", nextOpcodes[2], self.getRRegister(nextOpcodes[1]))
        pass

    def STRSEL(self, nextOpcodes):
        self.registers["sb"].selectionStart = nextOpcodes[1]
        self.registers["sb"].selectionLength = nextOpcodes[2]
        self.registers["pc"] += 3
        self.debugOutput("%d, %d" ,nextOpcodes[1], nextOpcodes[2])

    def STRINC(self, nextOpcodes):
        self.registers["sb"].selectionStart += 1
        self.registers["pc"] += 1
        self.debugOutput("")
        

    def LREADBYTE(self, nextOpcodes):
        self.registers["pc"] += 1
        self.debugOutput("")


    def READVAR(self, nextOpcodes):
        self.registers["pc"] += 2
        index = nextOpcodes[1]
        if (index == 14): # StringBuffer length
            self.setRRegister(0, self.registers["sb"].length)
            self.debugOutput("Read SB length: %d" , self.registers["sb"].length)
        elif (index == 17): # Get ASCII character at selection point
            self.setRRegister(0, ord(self.registers["sb"].data[self.registers["sb"].selectionStart]))
            self.debugOutput(" Got ASCII Character with value: %x", ord(self.registers["sb"].data[self.registers["sb"].selectionStart]))
        else:
            raise Exception("Not implemented!")


    def NOP(self, nextOpcodes):
        self.registers["pc"] += 1
        self.debugOutput("")
    
    def LSETI(self, nextOpcodes):
        self.setValueInARegister(struct.unpack('b', bytes(nextOpcodes[1:2]))[0])
        #self.registers[self.registers["A"]] = struct.unpack('b', bytes(nextOpcodes[1:2]))[0]
        self.registers["pc"] += 2
        self.debugOutput("Set Reg[A] = Reg[%d] = %d" , self.registers["A"], self.getValueInARegister())

    def EECALL(self, nextOpcodes):
        self.currentStackFrame += 1
        self.stackframe[self.currentStackFrame].returnAddr = self.registers["pc"]+2
        # Save function start for the current frame
        # needed for JMPs since they are relative to the function start
        self.stackframe[self.currentStackFrame].functionStart = nextOpcodes[1]*4 

        self.registers["pc"] = nextOpcodes[1]*4+1
        #if (self.registers["pc"] == 1021):
        #    self.registers["pc"] = 1020

        self.debugOutput("EECALL User Function %d" , nextOpcodes[1])

    def SELECTA(self, nextOpcodes):
        self.registers["A"] = nextOpcodes[1]
        self.registers["pc"] += 2
        self.debugOutput("Reg A = %d" , nextOpcodes[1])
        

    def WRBLK(self, nextOpcodes):
        numberOfValues = nextOpcodes[1]
        xAtStart = self.registers["X"]
        arraysToWrite = []
        self.registers["pc"] += 2+numberOfValues*4

        arraysToWrite = struct.unpack(">" + "I"*numberOfValues, bytes(nextOpcodes[2:2+numberOfValues*4]))
        for i in range(0, numberOfValues):
            self.setValueInXRegister(arraysToWrite[i])
            self.registers["X"] += 1

        self.debugOutput("Wrote %d values to Registers from %d" , numberOfValues, xAtStart)

    def SELECTX(self, nextOpcodes):
        self.registers["X"] = nextOpcodes[1]
        self.registers["pc"] += 2
        self.debugOutput("Reg X = %d" , nextOpcodes[1])

    def LOADIND(self, nextOpcodes):
        self.setRRegister(0, self.getRRegister(self.getRRegister(nextOpcodes[1])))
        self.registers["pc"] += 2
        self.debugOutput("Reg[0] = Reg[Reg[%d]]" , nextOpcodes[1])
        

    def EELOAD(self, nextOpcodes):
        self.setRRegister(nextOpcodes[1], self.eepromSlotToHex(nextOpcodes[2]))
        
        self.debugOutput("Register %d from slot %d with value: %x" , nextOpcodes[1], nextOpcodes[2], self.eepromSlotToHex(nextOpcodes[2]))
        self.registers["pc"] += 3

    def EELOADA(self, nextOpcodes):
        self.setValueInARegister(self.eepromSlotToHex(nextOpcodes[1]))
        
        self.debugOutput("Register A from slot %d with value: %x" , nextOpcodes[1], self.eepromSlotToHex(nextOpcodes[1]))
        self.registers["pc"] += 2

    def CLR(self, nextOpcodes):
        self.setRRegister(nextOpcodes[1], 0x00)
        
        self.debugOutput("Register %d = 0x00" , nextOpcodes[1])
        self.registers["pc"] += 2

    def CLR0(self, nextOpcodes):
        self.setRRegister(0, 0x00)
        
        self.debugOutput("Register 0 = 0x00" )
        self.registers["pc"] += 1

    def LMUL(self, nextOpcodes):
        self.setValueInARegister((self.getValueInARegister() * self.getRRegister(nextOpcodes[1])) & 0xffffffff)
        
        self.debugOutput("Reg[A] *= Reg[N] = %d",nextOpcodes[1])
        self.registers["pc"] += 2

    def STRSET(self, nextOpcodes):
        dataLength = 0x00
        while (nextOpcodes[dataLength+1] != 0x00):
            dataLength+=1
        pass

        self.registers["sb"].data = bytes(nextOpcodes[1:1+dataLength]).decode()
        self.registers["pc"] += 1+dataLength

    def STRFCHR(self, nextOpcodes):
        dataLength = 0x00
        while (nextOpcodes[dataLength+1] != 0x00):
            dataLength+=1
        
        self.registers["pc"] += dataLength+1
        self.registers["FS"] = bytes(nextOpcodes[1:1+dataLength]).decode()

        self.debugOutput("Set fieldseperator to %s" , self.registers["FS"])

    def STRFIELD(self, nextOpcodes):
        self.registers["pc"] += 2
        splitData = []
        for i in self.registers["FS"]:
            s = self.registers["sb"].data.split(i)
            for se in s:
                splitData.append(se)

        # Todo: Check the length of the split data...
        selectedData = splitData[nextOpcodes[1]-1]

        self.registers["sb"].selectionStart = self.registers["sb"].data.find(selectedData)
        self.registers["sb"].selectionEnd = self.registers["sb"].selectionStart + len(selectedData)

        self.debugOutput("Got seperator index 2: %s" ,selectedData)


    def EESAVEA(self, nextOpcodes):
        self.hexToEepromSlot(nextOpcodes[1], self.getValueInARegister())
        self.debugOutput("Register A with value %d write to slot: %d" , self.getValueInARegister(), nextOpcodes[1])
        self.registers["pc"] += 2
        
    def SELECTMB(self, nextOpcodes):
        self.registers["pc"] += 4
        self.registers["MB"] = [nextOpcodes[1],nextOpcodes[2], nextOpcodes[3]]
        self.debugOutput("Matrix Register %d with %d rows, %d columns" ,nextOpcodes[1],nextOpcodes[2], nextOpcodes[3])

    def SELECTMA(self, nextOpcodes):
        self.registers["pc"] += 4
        self.registers["MA"] = [nextOpcodes[1],nextOpcodes[2], nextOpcodes[3]]
        self.debugOutput("Matrix Register %d with %d rows, %d columns" ,nextOpcodes[1],nextOpcodes[2], nextOpcodes[3])
    
    def LUCMP2(self, nextOpcodes):
        self.registers["pc"] += 3
        v1 = self.getRRegister(nextOpcodes[1])
        v2 = self.getRRegister(nextOpcodes[2])

        if (v1 == v2):
            self.registers["S"] = "EQ"
        else:
            self.registers["S"] = "NE"

        self.debugOutput("CMP von %d mit %d" ,v1, v2)

    def LUCMPI(self, nextOpcodes):
        self.registers["pc"] += 2
        v1 = self.getValueInARegister()
        v2 = nextOpcodes[1]

        if (v1 == v2):
            self.registers["S"] = "EQ"
        else:
            self.registers["S"] = "NE"

        self.debugOutput("CMP von %d mit %d" ,v1, v2)

    def STRCMP(self, nextOpcodes):
        dataLength = 0x00
        while (nextOpcodes[dataLength+1] != 0x00):
            dataLength+=1
        
        self.registers["pc"] += dataLength+1
        s1 = bytes(nextOpcodes[1:1+dataLength])
        s2 = self.registers["sb"].data[self.registers["sb"].selectionStart:self.registers["sb"].selectionStart+dataLength].encode()

        if (s1 == s2):
            self.registers["S"] = "EQ"
        else:
            self.registers["S"] = "NE"

        self.debugOutput("STRCMP von %s mit %s" ,s1, s2)


    def BRACC(self, nextOpcodes):
        self.registers["pc"] += 3
        addrToJumpTo = struct.unpack('b', bytes(nextOpcodes[2:3]))[0]
        if (self.registers["S"] == "NE"):
            self.registers["pc"] += addrToJumpTo
        else:
            pass#self.registers["pc"] += 4
            
        self.debugOutput("mit COND" )


    def JMPCC(self, nextOpcodes):
        self.registers["pc"] += 4
        addrToJumpTo = nextOpcodes[2]*256+nextOpcodes[3]
        if (self.registers["S"] == "NE"):
            self.registers["pc"] = (self.stackframe[self.currentStackFrame].functionStart + 1)+addrToJumpTo
        else:
            #self.dumpCode("decrypted.bin")
            pass#self.registers["pc"] += 4
            
        self.debugOutput(" with COND %s" ,jmpccmapping[nextOpcodes[1]])

    def JMP(self, nextOpcodes):
        self.registers["pc"] += 3
        addrToJumpTo = nextOpcodes[1]*256+nextOpcodes[2]
        self.registers["pc"] = (self.stackframe[self.currentStackFrame].functionStart + 1)+addrToJumpTo
        
        self.debugOutput("JMP" )


    def MOP(self, nextOpcodes):
        self.registers["pc"] += 2
        self.debugOutput("Matrix Operation number: %s" , matrixOperationMapping[nextOpcodes[1]])

        offsetMatrixA = self.registers["MA"][0]
        offsetMatrixB = self.registers["MB"][0]
        lenMatrixA = self.registers["MA"][1]*self.registers["MA"][2]

        if (matrixOperationMapping[nextOpcodes[1]] == "COPYAB"):
            
            for i in range(0, lenMatrixA):
                self.setRRegister(offsetMatrixB+i, self.getRRegister(offsetMatrixA+i))

        if (matrixOperationMapping[nextOpcodes[1]] == "COPYBA"):
            for i in range(0, lenMatrixA):
                self.setRRegister(offsetMatrixA+i, self.getRRegister(offsetMatrixB+i))
        
        if (matrixOperationMapping[nextOpcodes[1]] == "TRANSPOSE"):
            matrixToTranspose = np.zeros(lenMatrixA)
            for i in range(0, lenMatrixA):
                matrixToTranspose[i] = self.getRRegister(offsetMatrixB+i)
            
            matrixToTranspose = np.reshape(matrixToTranspose, (self.registers["MA"][1],self.registers["MA"][2]))
            transposed = matrixToTranspose.T
            transposed = np.reshape(transposed, lenMatrixA)
            for i in range(0, lenMatrixA):
                self.setRRegister(offsetMatrixA+i, int(transposed[i]))

        if (matrixOperationMapping[nextOpcodes[1]] == "SCALAR_ADD"):
            for i in range(0, lenMatrixA):
                self.setRRegister(offsetMatrixA+i, self.getRRegister(offsetMatrixA+i) + self.getRRegister(0))


    def LSET0(self, nextOpcodes):
        self.registers["pc"] += 1
        self.setValueInARegister(self.getRRegister(0))
        self.debugOutput(" reg[A] = reg[0] = %d",self.getRRegister(0))

    def LTST0(self, nextOpcodes):
        self.registers["pc"] += 1
        v1 = self.getRRegister(0)
        v2 = self.getValueInARegister()

        if (v1 == v2):
            self.registers["S"] = "EQ"
        else:
            self.registers["S"] = "NE"
        
        self.debugOutput("Test %f == %f" ,v1,v2)

    def LONGUBYTE(self, nextOpcodes):
        self.registers["pc"] += 2
        self.setRRegister(0, nextOpcodes[1])
        self.debugOutput("Value: %d" ,nextOpcodes[1])

    def COPY0(self, nextOpcodes):
        self.registers["pc"] += 2
        self.setRRegister(nextOpcodes[1], self.getRRegister(0))
        self.debugOutput("Set Register %d to Value %d" ,nextOpcodes[1], self.getRRegister(0))

    def LONGUWORD(self, nextOpcodes):
        self.registers["pc"] += 3
        self.setRRegister(0, nextOpcodes[1]*256+nextOpcodes[2])
        self.debugOutput("Set Register 0 to Value %d" ,nextOpcodes[1]*256+nextOpcodes[2])

    def LSUB(self, nextOpcodes):
        self.registers["pc"] += 2
        self.debugOutput("A = %d - %d = %d" , self.getValueInARegister(), self.getRRegister(nextOpcodes[1]),self.getValueInARegister() - self.getRRegister(nextOpcodes[1]))
        self.setValueInARegister(self.getValueInARegister() - self.getRRegister(nextOpcodes[1]))

    def LADD(self, nextOpcodes):
        self.registers["pc"] += 2
        self.setValueInARegister(self.getValueInARegister() + self.getRRegister(nextOpcodes[1]))

        self.debugOutput("A = %d + %d = %d", self.getValueInARegister(), self.getRRegister(nextOpcodes[1]),self.getValueInARegister() + self.getRRegister(nextOpcodes[1]))


    def LSET(self, nextOpcodes):
        self.registers["pc"] += 2
        self.debugOutput("Set Reg[A] = %d" , nextOpcodes[1])
        self.setValueInARegister(self.getRRegister(nextOpcodes[1]))

    def LWRITE(self, nextOpcodes):
        self.registers["pc"] += 6
        value = self.unpackCode(nextOpcodes[2:6])
        self.debugOutput("Register %d to value %x" , nextOpcodes[1], value)
        self.setRRegister(nextOpcodes[1], value)

    def LWRITEA(self, nextOpcodes):
        self.registers["pc"] += 5
        value = self.unpackCode(nextOpcodes[1:5])
        self.debugOutput("Register A to value %x" , value)
        self.setValueInARegister(value)

    def FWRITEX(self, nextOpcodes):
        self.registers["pc"] += 5
        value = self.unpackCode(nextOpcodes[1:5])
        self.debugOutput("Register X to value %x" , value)
        self.setValueInXRegister(value)

    def LOR(self, nextOpcodes):
        self.registers["pc"] += 2
        self.debugOutput("Register A | %x == %x" , self.getRRegister(nextOpcodes[1]),self.getValueInARegister() | self.getRRegister(nextOpcodes[1]))
        self.setValueInARegister(self.getValueInARegister() | self.getRRegister(nextOpcodes[1]))

    def LAND(self, nextOpcodes):
        self.registers["pc"] += 2
        self.debugOutput("Register A & %x == %x" , self.getRRegister(nextOpcodes[1]),self.getValueInARegister() & self.getRRegister(nextOpcodes[1]))
        self.setValueInARegister(self.getValueInARegister() & self.getRRegister(nextOpcodes[1]))

    def LXOR(self, nextOpcodes):
        self.registers["pc"] += 2
        self.debugOutput("Register A ^ %x => %d ^ %d = %d " , self.getRRegister(nextOpcodes[1]), self.getValueInARegister(), self.getRRegister(nextOpcodes[1]), self.getValueInARegister() ^ self.getRRegister(nextOpcodes[1]))
        self.setValueInARegister(self.getValueInARegister() ^ self.getRRegister(nextOpcodes[1]))

    def SAVEIND(self, nextOpcodes):
        self.registers["pc"] += 2
        self.setRRegister(self.getRRegister(nextOpcodes[1]), self.getValueInARegister())
        self.debugOutput("")

    def LINC(self, nextOpcodes):
        self.registers["pc"] += 2
        self.setRRegister(nextOpcodes[1], self.getRRegister(nextOpcodes[1]) + 1)
        self.debugOutput("Register %d += 1 == %d" ,nextOpcodes[1],self.getRRegister(nextOpcodes[1]))

    def LDEC(self, nextOpcodes):#
        self.registers["pc"] += 2
        self.setRRegister(nextOpcodes[1], self.getRRegister(nextOpcodes[1]) - 1)
        self.debugOutput("Register %d -= 1 == %d" ,nextOpcodes[1],self.getRRegister(nextOpcodes[1]))


    def RET(self, nextOpcodes):
        self.registers["pc"] = self.stackframe[self.currentStackFrame].returnAddr
        self.currentStackFrame -= 1
        if (self.currentStackFrame == -1):
            self.isRunning = False
        self.debugOutput("RET to %d" ,self.registers["pc"])

    def RESET(self, nextOpcodes):
        self.registers["pc"] += 1
        
        self.debugOutput(" as NOP" )


    def LSHIFT(self, nextOpcodes):
        self.registers["pc"] += 2
        shiftCount = self.getRRegister(nextOpcodes[1])
        valueBeforeShift = self.getValueInARegister()
        if (shiftCount > 0):
            self.setValueInARegister(self.getValueInARegister() << self.getRRegister(nextOpcodes[1]))
        else:
            self.setValueInARegister(self.getValueInARegister() >> -self.getRRegister(nextOpcodes[1]))
        self.debugOutput("0x%x << 0x%x == 0x%x" , valueBeforeShift, self.getRRegister(nextOpcodes[1]),self.getValueInARegister())

def main():
    if (len(sys.argv) < 2):
        print("Usage: emulator.py [opcodes.bin]")
        exit(0)

    # Read the instructions from the binary file
    instructions = bytearray(open(sys.argv[1], "rb").read())
    # Pad the instructions to 1024 bytes since we use the same array for the R/W at block 255
    instructions += bytearray(b"\x00"*(1024-len(instructions)))

    e = Emulator(instructions)
    e.debug = True

    # Set Stringbuffer (sb) input data
    e.registers["sb"].setData("DrgnS{uMFlagPwningUnit}")

    # Run until the program terminates
    e.run()

    # Read result in string buffer
    print("Result in String Buffer was: %s" % e.registers["sb"].data)


if __name__== "__main__":
  main()