using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Bonsai.Api.Samples.Cartpole
{
    class Program
    {
        public static void Main(string[] args)
        {

            Console.WriteLine("Enter 0 for EventProgram or 1 for LoopProgram:");
            string choice = Console.ReadLine();

            if(choice == "0")
            {
                Console.WriteLine("Starting event program...");
                EventProgram.RunMain(args).Wait();
            }
            else if (choice == "1")
            {
                Console.WriteLine("Starting loop program...");
                LoopProgram.RunMain(args);
            }
            else
            {
                Console.WriteLine("Bye, bye");
            }
        }
    }
}
