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
        }
    }
}