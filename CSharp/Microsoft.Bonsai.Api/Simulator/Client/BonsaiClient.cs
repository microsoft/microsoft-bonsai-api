// ------------------------------------------------------------
//  Copyright (c) Microsoft Corporation.  All rights reserved.
//  Author: maygup
//  Date: 06/23/2020
// ------------------------------------------------------------

namespace Microsoft.Bonsai.SimulatorApi.Client
{
    using System;
    using System.Net.Http;
    using System.Threading;
    using System.Threading.Tasks;
    using Microsoft.Bonsai.SimulatorApi;
    using Microsoft.Bonsai.SimulatorApi.Models;
    using Microsoft.Rest.TransientFaultHandling;

    /// <summary>
    /// Bonsai API client for simulators to talk to Bonsai platform.
    /// example pattern to use is:
    /// BonsaiClientConfig config = new BonsaiClientConfig(...);
    /// BonsaiClient client = new BonsaiClient(config); 
    /// client.Session.CreateAsync(...);
    /// </summary>
    public class BonsaiClient : SimulatorAPI
    {
        private static BonsaiClientConfig config;

        public EventHandler<EpisodeStartEventArgs> EpisodeStart;
        public EventHandler<EpisodeStepEventArgs> EpisodeStep;
        public EventHandler<EpisodeFinishEventArgs> EpisodeFinish;

        /// <summary>
        /// Currently handles authentication and logging. But we can add other logic in this interceptor as well.
        /// </summary>
        private class CustomRequestHandler : DelegatingHandler
        {
            protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
            {
                if (BonsaiClient.config.EnableLogging)
                {
                    Console.WriteLine(request);
                }

                //
                // Handle Authentication for the request.
                //
                if (!string.IsNullOrEmpty(BonsaiClient.config.AccessKey))
                {
                    if (request.Headers.Contains("Authorization"))
                    {
                        request.Headers.Remove("Authorization");
                    }

                    request.Headers.TryAddWithoutValidation("Authorization", new [] { config.AccessKey });
                }
                
                var response = await base.SendAsync(request, cancellationToken);
                
                if (BonsaiClient.config.EnableLogging)
                {
                    Console.WriteLine(response);
                }
                
                return response;
            }
        }
        
        public BonsaiClient(BonsaiClientConfig config) : base(handlers: new [] { new CustomRequestHandler() })
        {
            if (string.IsNullOrEmpty(config.AccessKey))
            {
                throw new System.Exception("AccessKey not set in config!");
            }

            if (string.IsNullOrEmpty(config.Workspace))
            {
                throw new System.Exception("Bonsai workspace not set in config!");
            }

            BonsaiClient.config = config;

            var retryPolicy = new RetryPolicy(new TransientErrorIgnoreStrategy(), new ExponentialBackoffRetryStrategy());
            this.SetRetryPolicy(retryPolicy);
        }


        public async Task Connect(IModel model)
        {
            SimulatorInterface sim_interface = new SimulatorInterface();

            sim_interface.Name = "CSharp-Simulator";
            sim_interface.Timeout = 60;
            sim_interface.Capabilities = null;

            await Connect(sim_interface, model);
        }

        public async Task Connect(SimulatorInterface sim_interface, IModel model)
        {
            await Task.Run(() => {
                // object that indicates if we have registered successfully
                object registered = null;
                string sessionId = "";
                int sequenceId = 1;

                while (true)
                {
                    // go through the registration process
                    if (registered == null)
                    {
                        var sessions = this.Session;

                        // minimum required
                        sim_interface.SimulatorContext = BonsaiClient.config.SimulatorContext;

                        var registrationResponse = sessions.CreateWithHttpMessagesAsync(BonsaiClient.config.Workspace, sim_interface).Result;

                        if (registrationResponse.Body.GetType() == typeof(SimulatorSessionResponse))
                        {
                            registered = registrationResponse;

                            SimulatorSessionResponse sessionResponse = registrationResponse.Body;

                            // this is required
                            sessionId = sessionResponse.SessionId;
                        }

                        Console.WriteLine(DateTime.Now + " - registered session " + sessionId);

                    }
                    else // now we are registered
                    {
                        Console.WriteLine(DateTime.Now + " - advancing " + sequenceId);

                        // build the SimulatorState object
                        SimulatorState simState = new SimulatorState();
                        simState.SequenceId = sequenceId; // required
                        simState.State = model.State; // required
                        simState.Halted = model.Halted; // required

                        try
                        {
                            // advance only returns an object, so we need to check what type of object
                            var response = this.Session.AdvanceWithHttpMessagesAsync(BonsaiClient.config.Workspace, sessionId, simState).Result;

                            // if we get an error during advance
                            if (response.Body.GetType() == typeof(EventModel))
                            {

                                EventModel eventModel = (EventModel)response.Body;
                                Console.WriteLine(DateTime.Now + " - received event: " + eventModel.Type);
                                sequenceId = eventModel.SequenceId; // get the sequence from the result

                                // now check the type of event and handle accordingly

                                if (eventModel.Type == EventType.EpisodeStart)
                                {
                                    OnEpisodeStart(new EpisodeStartEventArgs() { Config = eventModel.EpisodeStart.Config });
                                }
                                else if (eventModel.Type == EventType.EpisodeStep)
                                {
                                    OnEpisodeStep(new EpisodeStepEventArgs() { Action = eventModel.EpisodeStep.Action });
                                }
                                else if (eventModel.Type == EventType.EpisodeFinish)
                                {
                                    // Console.WriteLine("Episode Finish");
                                    OnEpisodeFinish(new EpisodeFinishEventArgs() { EpisodeFinishReason = eventModel.EpisodeFinish.Reason });
                                }
                                else if (eventModel.Type == EventType.Idle)
                                {
                                    Thread.Sleep(Convert.ToInt32(eventModel.Idle.CallbackTime) * 1000);
                                }
                                else if (eventModel.Type == EventType.Unregister)
                                {
                                    try
                                    {
                                        this.Session.DeleteWithHttpMessagesAsync(BonsaiClient.config.Workspace, sessionId).Wait();
                                    }
                                    catch (Exception ex)
                                    {
                                        Console.WriteLine("cannot unregister: " + ex.Message);
                                    }
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("Error occurred at " + DateTime.UtcNow + ":");
                            Console.WriteLine(ex.ToString());
                            Console.WriteLine("Simulation will now end");
                            Environment.Exit(0);
                        }
                    }
                }
            });
        }

        protected virtual void OnEpisodeStart(EpisodeStartEventArgs args)
        {
            if (EpisodeStart != null)
            {
                EpisodeStart(this, args);
            }

        }

        protected virtual void OnEpisodeStep(EpisodeStepEventArgs args)
        {
            
            if (EpisodeStep != null)
            {
                EpisodeStep(this, args);
            }

        }

        protected virtual void OnEpisodeFinish(EpisodeFinishEventArgs args)
        {

            if (EpisodeFinish != null)
            {
                EpisodeFinish(this, args);
            }

        }

    }

    public interface IModel
    {
        object State { get;}
        bool? Halted { get; }
    }

    public class EpisodeStartEventArgs : EventArgs
    {
        public object Config { get; set; } 
    }

    public class EpisodeStepEventArgs : EventArgs 
    { 
        public object Action { get; set; }
    }

    public class IdleEventArgs : EventArgs
    {

    }

    public class EpisodeFinishEventArgs : EventArgs 
    {
        public EpisodeFinishReason? EpisodeFinishReason { get; set; }
    }

    public class UnregisterEventArgs : EventArgs
    {
        public UnregisterReason? UnregisterReason { get; set; }
    }
}