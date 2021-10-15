using Microsoft.Bonsai.SimulatorApi.Client;
using Microsoft.Bonsai.SimulatorApi.Models;
using System;
using Newtonsoft.Json;
using System.Net.Http;
using System.Threading;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Bonsai.Api.Samples.Cartpole
{
    class Program
    {
        //the cartpole model
        private static Model model = new Model();

        /// <summary>
        /// 
        /// </summary>
        /// <param name="args"></param>
        /// <remarks>
        /// You can run the example by itself, or pass the predict and http://localhost:5000/v1/prediction url 
        /// </remarks>
        static void Main(string[] args)
        {
            if (args.Length == 0)
                TrainAndAssess();
            else
            {
                if (args[0] == "predict")
                    RunPrediction(args[1]);//assumes the second value is the URL
            }
        }

        /// <summary>
        /// Run the Train or Assessment loop
        /// </summary>
        private static void TrainAndAssess()
        {
            
            String workspaceName = GetWorkspace();
            String accessKey = GetAccessKey();

            BonsaiClientConfig bcConfig = new BonsaiClientConfig(workspaceName, accessKey);
            BonsaiClient client = new BonsaiClient(bcConfig);

            client.EpisodeStart += (o,e) => { Config config = new Config(); model.Start(config); };
            client.EpisodeStep += (o, e) => 
            {
                Action action = new Action();
                dynamic stepAction = e.Action;
                action.Command = stepAction.command.Value;

                // move the model forward
                model.Step(action);

            };

            client.EpisodeFinish += (o,e) => { Console.WriteLine(e.EpisodeFinishReason.ToString()); };

            Task.Run(() => client.Connect(model));

            Console.ReadLine(); //hold open the console
        }

        private static void RunPrediction(string predictionurl)
        {
            Model model = new Model();

            HttpClient bc = new HttpClient();

            while (true)
            {
                // create the request object -- using random numbers in the state range
                string reqJson = JsonConvert.SerializeObject(model.State);

                var request = new HttpRequestMessage()
                {
                    Method = HttpMethod.Get,
                    RequestUri = new Uri(predictionurl),
                    Content = new StringContent(reqJson, Encoding.UTF8, "application/json")
                };

                var resp = bc.SendAsync(request).Result;
                resp.EnsureSuccessStatusCode();

                var respJson = resp.Content.ReadAsStringAsync().Result;

                // convert the json string to a dynamic object with Kp and Ki types
                Action resultObj = (Action)JsonConvert.DeserializeObject(respJson);

                Console.WriteLine($"Kp = {resultObj.Command}");
                model.Step(resultObj);
            }

        }

        private static string GetWorkspace()
        {

            if (Environment.GetEnvironmentVariable("SIM_WORKSPACE") != null)
            {
                return Environment.GetEnvironmentVariable("SIM_WORKSPACE");
            }

            //fill in your Bonsai workspace ID
            return "<your_bonsai_workspace_id>";
        }

        private static String GetAccessKey()
        {

            if (Environment.GetEnvironmentVariable("SIM_ACCESS_KEY") != null)
            {
                return Environment.GetEnvironmentVariable("SIM_ACCESS_KEY");
            }

            //fill in your Bonsai access key
            return "<your_bonsai_access_key>";
        }
    }
}
