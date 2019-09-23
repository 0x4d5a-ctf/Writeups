import struct

matrixOperationMapping = {0:"SCALAR_SET",1:"SCALAR_ADD",2:"SCALAR_SUB",3:"SCALAR_SUBR",4:"SCALAR_MUL",5:"SCALAR_DIV",6:"SCALAR_DIVR",7:"SCALAR_POW",8:"EWISE_SET",9:"EWISE_ADD",10:"EWISE_SUB",11:"EWISE_SUBR",12:"EWISE_MUL",13:"EWISE_DIV",14:"EWISE_DIVR",15:"EWISE_POW",16:"MULTIPLY",17:"IDENTITY",18:"DIAGONAL",19:"TRANSPOSE",20:"COUNT", 25:"COPYAB", 27:"COPYBA"}

jmpccmapping = {0x51:"ZEQ", 0x50:"NEQ",0x72:"LT",0x62:"LE",0x70:"GT",0x60:"GE"}
opcodeDict = {
"NOP":0x00, # No Operation
"SELECTA":0x01, # Select register A
"SELECTX":0x02, # Select register X
"CLR":0x03, # reg[nn] = 0
"CLRA":0x04, # reg[A] = 0
"CLRX":0x05, # reg[X] = 0, X = X + 1
"CLR0":0x06, # reg[0] = 0
"COPY":0x07, # reg[nn] = reg[mm]
"COPYA":0x08, # reg[nn] = reg[A]
"COPYX":0x09, # reg[nn] = reg[X], X = X + 1
"LOAD":0x0A, # reg[0] = reg[nn]
"LOADA":0x0B, # reg[0] = reg[A]
"LOADX":0x0C, # reg[0] = reg[X], X = X + 1
"ALOADX":0x0D, # reg[A] = reg[X], X = X + 1
"XSAVE":0x0E, # reg[X] = reg[nn], X = X + 1
"XSAVEA":0x0F, # reg[X] = reg[A], X = X + 1
"COPY0":0x10, # reg[nn] = reg[0]
"COPYI":0x11, # reg[nn] = long(unsigned bb)
"SWAP":0x12, # Swap reg[nn] and reg[mm]
"SWAPA":0x13, # Swap reg[A] and reg[nn]
"LEFT":0x14, # Left parenthesis
"RIGHT":0x15, # Right parenthesis
"FWRITE":0x16, # Write 32-bit float to reg[nn]
"FWRITEA":0x17, # Write 32-bit float to reg[A]
"FWRITEX":0x18, # Write 32-bit float to reg[X], X = X + 1
"FWRITE0":0x19, # Write 32-bit float to reg[0]
"FREAD":0x1A, # Read 32-bit float from reg[nn]
"FREADA":0x1B, # Read 32-bit float from reg[A]
"FREADX":0x1C, # Read 32-bit float from reg[X], X = X + 1
"FREAD0":0x1D, # Read 32-bit float from reg[0]
"ATOF":0x1E, # Convert ASCII to float, store in reg[0]
"FTOA":0x1F, # Convert float to ASCII
"FSET":0x20, # reg[A] = reg[nn]
"FADD":0x21, # reg[A] = reg[A] + reg[nn]
"FSUB":0x22, # reg[A] = reg[A] - reg[nn]
"FSUBR":0x23, # reg[A] = reg[nn] - reg[A]
"FMUL":0x24, # reg[A] = reg[A] * reg[nn]
"FDIV":0x25, # reg[A] = reg[A] / reg[nn]
"FDIVR":0x26, # reg[A] = reg[nn] / reg[A]
"FPOW":0x27, # reg[A] = reg[A] ** reg[nn]
"FCMP":0x28, # Float compare reg[A] - reg[nn]
"FSET0":0x29, # reg[A] = reg[0]
"FADD0":0x2A, # reg[A] = reg[A] + reg[0]
"FSUB0":0x2B, # reg[A] = reg[A] - reg[0]
"FSUBR0":0x2C, # reg[A] = reg[0] - reg[A]
"FMUL0":0x2D, # reg[A] = reg[A] * reg[0]
"FDIV0":0x2E, # reg[A] = reg[A] / reg[0]
"FDIVR0":0x2F, # reg[A] = reg[0] / reg[A]
"FPOW0":0x30, # reg[A] = reg[A] ** reg[0]
"FCMP0":0x31, # Float compare reg[A] - reg[0]
"FSETI":0x32, # reg[A] = float(bb)
"FADDI":0x33, # reg[A] = reg[A] + float(bb)
"FSUBI":0x34, # reg[A] = reg[A] - float(bb)
"FSUBRI":0x35, # reg[A] = float(bb) - reg[A]
"FMULI":0x36, # reg[A] = reg[A] * float(bb)
"FDIVI":0x37, # reg[A] = reg[A] / float(bb)
"FDIVRI":0x38, # reg[A] = float(bb) / reg[A]
"FPOWI":0x39, # reg[A] = reg[A] ** bb
"FCMPI":0x3A, # Float compare reg[A] - float(bb)
"FSTATUS":0x3B, # Float status of reg[nn]
"FSTATUSA":0x3C, # Float status of reg[A]
"FCMP2":0x3D, # Float compare reg[nn] - reg[mm]
"FNEG":0x3E, # reg[A] = -reg[A]
"FABS":0x3F, # reg[A] = | reg[A] |
"FINV":0x40, # reg[A] = 1 / reg[A]
"SQRT":0x41, # reg[A] = sqrt(reg[A])
"ROOT":0x42, # reg[A] = root(reg[A], reg[nn])
"LOG":0x43, # reg[A] = log(reg[A])
"LOG10":0x44, # reg[A] = log10(reg[A])
"EXP":0x45, # reg[A] = exp(reg[A])
"EXP10":0x46, # reg[A] = exp10(reg[A])
"SIN":0x47, # reg[A] = sin(reg[A])
"COS":0x48, # reg[A] = cos(reg[A])
"TAN":0x49, # reg[A] = tan(reg[A])
"ASIN":0x4A, # reg[A] = asin(reg[A])
"ACOS":0x4B, # reg[A] = acos(reg[A])
"ATAN":0x4C, # reg[A] = atan(reg[A])
"ATAN2":0x4D, # reg[A] = atan2(reg[A], reg[nn])
"DEGREES":0x4E, # reg[A] = degrees(reg[A])
"RADIANS":0x4F, # reg[A] = radians(reg[A])
"FMOD":0x50, # reg[A] = reg[A] MOD reg[nn]
"FLOOR":0x51, # reg[A] = floor(reg[A])
"CEIL":0x52, # reg[A] = ceil(reg[A])
"ROUND":0x53, # reg[A] = round(reg[A])
"FMIN":0x54, # reg[A] = min(reg[A], reg[nn])
"FMAX":0x55, # reg[A] = max(reg[A], reg[nn])
"FCNV":0x56, # reg[A] = conversion(nn, reg[A])
"FMAC":0x57, # reg[A] = reg[A] + (reg[nn] * reg[mm])
"FMSC":0x58, # reg[A] = reg[A] - (reg[nn] * reg[mm])
"LOADBYTE":0x59, # reg[0] = float(signed bb)
"LOADUBYTE":0x5A, # reg[0] = float(unsigned byte)
"LOADWORD":0x5B, # reg[0] = float(signed word)
"LOADUWORD":0x5C, # reg[0] = float(unsigned word)
"LOADE":0x5D, # reg[0] = 2.7182818
"LOADPI":0x5E, # reg[0] = 3.1415927
"LOADCON":0x5F, # reg[0] = float constant(nn)
"FLOAT":0x60, # reg[A] = float(reg[A])
"FIX":0x61, # reg[A] = fix(reg[A])
"FIXR":0x62, # reg[A] = fix(round(reg[A]))
"FRAC":0x63, # reg[A] = fraction(reg[A])
"FSPLIT":0x64, # reg[A] = int(reg[A]), reg[0] = frac(reg[A])
"SELECTMA":0x65, # Select matrix A
"SELECTMB":0x66, # Select matrix B
"SELECTMC":0x67, # Select matrix C
"LOADMA":0x68, # reg[0] = matrix A[bb,bb]
"LOADMB":0x69, # reg[0] = matrix B[bb, bb]
"LOADMC":0x6A, # reg[0] = matrix C[bb, bb]
"SAVEMA":0x6B, # matrix A[bb,bb] = reg[A]
"SAVEMB":0x6C, # matrix B[bb,bb] = reg[A]
"SAVEMC":0x6D, # matrix C[bb,bb] = reg[A]
"MOP":0x6E, # Matrix operation
"FFT":0x6F, # FFT operation
"WRBLK":0x70, # write register block
"RDBLK":0x71, # read register block
"LOADIND":0x7A, # reg[0] = reg[reg[nn]]
"SAVEIND":0x7B, # reg[reg[nn]] = reg[A]
"INDA":0x7C, # Select A using reg[nn]
"INDX":0x7D, # Select X using reg[nn]
"FCALL":0x7E, # Call function in Flash memory
"EECALL":0x7F, # Call function in EEPROM memory
"RET":0x80, # Return from function
"BRA":0x81, # Unconditional branch
"BRACC":0x82, # Conditional branch
"JMP":0x83, # Unconditional jump
"JMPCC":0x84, # Conditional jump
"TABLE":0x85, # Table lookup
"FTABLE":0x86, # Floating point reverse table lookup
"LTABLE":0x87, # Long integer reverse table lookup
"POLY":0x88, # reg[A] = nth order polynomial
"GOTO":0x89, # Computed goto
"RETCC":0x8A, # Conditional return from function
"LWRITE":0x90, # Write 32-bit long integer to reg[nn]
"LWRITEA":0x91, # Write 32-bit long integer to reg[A]
"LWRITEX":0x92, # Write 32-bit long integer to reg[X], X = X + 1
"LWRITE0":0x93, # Write 32-bit long integer to reg[0]
"LREAD":0x94, # Read 32-bit long integer from reg[nn]
"LREADA":0x95, # Read 32-bit long integer from reg[A]
"LREADX":0x96, # Read 32-bit long integer from reg[X], X = X + 1
"LREAD0":0x97, # Read 32-bit long integer from reg[0]
"LREADBYTE":0x98, # Read lower 8 bits of reg[A]
"LREADWORD":0x99, # Read lower 16 bits reg[A]
"ATOL":0x9A, # Convert ASCII to long integer
"LTOA":0x9B, # Convert long integer to ASCII
"LSET":0x9C, # reg[A] = reg[nn]
"LADD":0x9D, # reg[A] = reg[A] + reg[nn]
"LSUB":0x9E, # reg[A] = reg[A] - reg[nn]
"LMUL":0x9F, # reg[A] = reg[A] * reg[nn]
"LDIV":0xA0, # reg[A] = reg[A] / reg[nn]
"LCMP":0xA1, # Signed long compare reg[A] - reg[nn]
"LUDIV":0xA2, # reg[A] = reg[A] / reg[nn]
"LUCMP":0xA3, # Unsigned long compare of reg[A] - reg[nn]
"LTST":0xA4, # Long integer status of reg[A] AND reg[nn] 
"LSET0":0xA5, # reg[A] = reg[0]
"LADD0":0xA6, # reg[A] = reg[A] + reg[0]
"LSUB0":0xA7, # reg[A] = reg[A] - reg[0]
"LMUL0":0xA8, # reg[A] = reg[A] * reg[0]
"LDIV0":0xA9, # reg[A] = reg[A] / reg[0]
"LCMP0":0xAA, # Signed long compare reg[A] - reg[0]
"LUDIV0":0xAB, # reg[A] = reg[A] / reg[0]
"LUCMP0":0xAC, # Unsigned long compare reg[A] - reg[0]
"LTST0":0xAD, # Long integer status of reg[A] AND reg[0] 
"LSETI":0xAE, # reg[A] = long(bb)
"LADDI":0xAF, # reg[A] = reg[A] + long(bb)
"LSUBI":0xB0, # reg[A] = reg[A] - long(bb)
"LMULI":0xB1, # reg[A] = reg[A] * long(bb)
"LDIVI":0xB2, # reg[A] = reg[A] / long(bb)
"LCMPI":0xB3, # Signed long compare reg[A] - long(bb)
"LUDIVI":0xB4, # reg[A] = reg[A] / unsigned long(bb)
"LUCMPI":0xB5, # Unsigned long compare reg[A] - ulong(bb)
"LTSTI":0xB6, # Long integer status of reg[A] AND ulong(bb)
"LSTATUS":0xB7, # Long integer status of reg[nn]
"LSTATUSA":0xB8, # Long integer status of reg[A]
"LCMP2":0xB9, # Signed long compare reg[nn] - reg[mm]
"LUCMP2":0xBA, # Unsigned long compare reg[nn] - reg[mm]
"LNEG":0xBB, # reg[A] = -reg[A]
"LABS":0xBC, # reg[A] = | reg[A] |
"LINC":0xBD, # reg[nn] = reg[nn] + 1
"LDEC":0xBE, # reg[nn] = reg[nn] - 1
"LNOT":0xBF, # reg[A] = NOT reg[A]
"LAND":0xC0, # reg[A] = reg[A] AND reg[nn]
"LOR":0xC1, # reg[A] = reg[A] OR reg[nn]
"LXOR":0xC2, # reg[A] = reg[A] XOR reg[nn]
"LSHIFT":0xC3, # reg[A] = reg[A] shift reg[nn]
"LMIN":0xC4, # reg[A] = min(reg[A], reg[nn])
"LMAX":0xC5, # reg[A] = max(reg[A], reg[nn])
"LONGBYTE":0xC6, # reg[0] = long(signed byte bb)
"LONGUBYTE":0xC7, # reg[0] = long(unsigned byte bb)
"LONGWORD":0xC8, # reg[0] = long(signed word wwww)
"LONGUWORD":0xC9, # reg[0] = long(unsigned word wwww)
"SETSTATUS":0xCD, # Set status byte
"SEROUT":0xCE, # Serial output
"SERIN":0xCF, # Serial Input
"SETOUT":0xD0, # Set OUT1 and OUT2 output pins
"ADCMODE":0xD1, # Set A/D trigger mode
"ADCTRIG":0xD2, # A/D manual trigger
"ADCSCALE":0xD3, # ADCscale[ch] = B
"ADCLONG":0xD4, # reg[0] = ADCvalue[ch]
"ADCLOAD":0xD5, # reg[0] = float(ADCvalue[ch]) * ADCscale[ch]
"ADCWAIT":0xD6, # wait for next A/D sample
"TIMESET":0xD7, # time = reg[0]
"TIMELONG":0xD8, # reg[0] = time (long)
"TICKLONG":0xD9, # reg[0] = ticks (long)
"EESAVE":0xDA, # EEPROM[nn] = reg[mm]
"EESAVEA":0xDB, # EEPROM[nn] = reg[A]
"EELOAD":0xDC, # reg[nn] = EEPROM[mm]
"EELOADA":0xDD, # reg[A] = EEPROM[nn]
"EEWRITE":0xDE, # Store bytes in EEPROM
"EXTSET":0xE0, # external input count = reg[0]
"EXTLONG":0xE1, # reg[0] = external input counter (long)
"EXTWAIT":0xE2, # wait for next external input
"STRSET":0xE3, # Copy string to string buffer
"STRSEL":0xE4, # Set selection point
"STRINS":0xE5, # Insert string at selection point
"STRCMP":0xE6, # Compare string with string buffer
"STRFIND":0xE7, # Find string and set selection point
"STRFCHR":0xE8, # Set field separators
"STRFIELD":0xE9, # Find field and set selection point
"STRTOF":0xEA, # Convert string selection to float
"STRTOL":0xEB, # Convert string selection to long
"READSEL":0xEC, # Read string selection
"STRBYTE":0xED, # Insert 8-bit byte at selection point
"STRINC":0xEE, # increment selection point
"STRDEC":0xEF, # decrement selection point
"SYNC":0xF0, # Get synchronization byte
"READSTATUS":0xF1, # Read status byte
"READSTR":0xF2, # Read string from string buffer
"VERSION":0xF3, # Copy version string to string buffer
"IEEEMODE":0xF4, # Set IEEE mode (default)
"PICMODE":0xF5, # Set PIC mode
"CHECKSUM":0xF6, # Calculate checksum for uM-FPU code
"BREAK":0xF7, # Debug breakpoint
"TRACEOFF":0xF8, # Turn debug trace off
"TRACEON":0xF9, # Turn debug trace on
"TRACESTR":0xFA, # Send string to debug trace buffer
"TRACEREG":0xFB, # Send register value to trace buffer
"READVAR":0xFC, # Read internal variable, store in reg[0]
"RESET":0xFF, # No operation (9 consecutive FF bytes cause a reset)

"SYNC_CHAR":0x5C # sync character
}

def getOpcodeByByte(byteToFind):
  for name, byte in opcodeDict.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
    if byte == byteToFind:
       return (name, byte)