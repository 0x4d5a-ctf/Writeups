using System;

namespace myApp
{
    class Program
        {
            static void Main(string[] args)
            {
                Loop();
                Console.WriteLine("I am here.");
            }

            unsafe static void Loop()
            {
            	
            	long* offset = stackalloc long[32];
            	long* doLoop = stackalloc long[32];
            	long* p = stackalloc long[32];
            	*doLoop = 1;
            	
                


                *offset = (long)p;
                while (*doLoop != 0)
                {
                    Console.WriteLine("Input: ");
                    var s = Console.ReadLine();

                    switch (s)
                    {
                        case "I":
                            p++;
                            break;


                        case "R":
                            p = (long*)*offset;
                            break;

                        case "P":
                            Console.WriteLine(*p);
                            break;

                        case "W":
                            var value = Convert.ToInt64(Console.ReadLine(),16);
                            *p = value;
                            break;

                       /* case "L":
                        	Console.WriteLine("Pointer: 0x{0:X}", (long)p);
                        	//Console.WriteLine("Offset: 0x{0:X}", (long)offset);
                        	Console.WriteLine("Loop: 0x{0:X}", (long)doLoop);
                            break;*/

                    }
                }
                /*try
                {
                    int* p = stackalloc int[32];
                    int i = 40;
                    while (i > 0)
                    {
                        *p++ = 0x41414141;
                        --i;
                    }
                }
                catch (Exception)
                {
                    Console.WriteLine("Exception caught.");
                }
                Console.WriteLine("Finished buffer overflow attack");*/

            }
        }
}
