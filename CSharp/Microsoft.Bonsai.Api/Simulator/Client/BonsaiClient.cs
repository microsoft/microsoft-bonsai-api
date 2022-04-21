// ------------------------------------------------------------
//  Copyright (c) Microsoft Corporation. All rights reserved.
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
    using System.Collections.Generic;
    using Microsoft.Rest;
    using Microsoft.Extensions.Logging;
    using Microsoft.Extensions.DependencyInjection;

    /// <summary>
    /// Bonsai API client for simulators to talk to Bonsai platform.
    /// example pattern to use is:
    /// BonsaiClientConfig config = new BonsaiClientConfig(...);
    /// BonsaiClient client = new BonsaiClient(config);
    /// client.Session.CreateAsync(...);
    /// </summary>
    public class BonsaiClient : SimulatorAPI
    {
        ISession realSessionOperations;

        public new ISession Session { get; private set; }

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

                    request.Headers.TryAddWithoutValidation("Authorization", new[] { config.AccessKey });
                }

                HttpResponseMessage response = await base.SendAsync(request, cancellationToken);

                if (BonsaiClient.config.EnableLogging || !response.IsSuccessStatusCode)
                {
                    Console.WriteLine(response);
                }

                return response;
            }
        }

        public BonsaiClient(BonsaiClientConfig config) : base(handlers: new[] { new CustomRequestHandler() })
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

            //
            // TODO: Get an ILogger!
            this.realSessionOperations = base.Session;
            this.Session = new SessionOperationsWrapper(this.realSessionOperations);
        }

        protected class SessionOperationsWrapper : ISession
        {
            protected static async Task<TRet> WrapSessionOperation<TRet>(
                string operationName,
                Func<Task<TRet>> func,
                ILogger logger = null
                )
            {
                try
                {
                    //
                    // [NoCancellationTokenForAsyncMethod] - The function is supposed to supply it
                    //
                    #pragma warning disable NoCancellationTokenForAsyncMethod
                    return await func().ConfigureAwait(false);
                }
                catch (Exception ex)
                {
                    if (logger != null)
                    {
                        logger.LogError(ex, "Error when calling Session.{0}", operationName);
                    }
                    throw;
                }
            }

            private readonly ISession realOps;
            private readonly ILogger logger;

            public SessionOperationsWrapper(ISession realOps, ILogger logger = null)
            {
                this.realOps = realOps;
                this.logger = logger;

                ServiceProvider serviceProvider = new ServiceCollection()
                    .AddLogging(c => c.AddConsole(opt => opt.LogToStandardErrorThreshold = LogLevel.Debug))
                    .BuildServiceProvider();

                if (logger == null)
                {
                    this.logger = serviceProvider.GetService<ILoggerFactory>().CreateLogger<ISession>();
                }
            }

            /// <inheritdoc/>
            public async Task<HttpOperationResponse<IList<SimulatorSessionSummary>>> ListWithHttpMessagesAsync(string workspaceName, string deploymentMode = default(string), string sessionStatus = default(string), string collection = default(string), string package = default(string), Dictionary<string, List<string>> customHeaders = null, CancellationToken cancellationToken = default(CancellationToken))
            {
                return await WrapSessionOperation<HttpOperationResponse<IList<SimulatorSessionSummary>>>(
                    "List",
                    async () => await this.realOps.ListWithHttpMessagesAsync(workspaceName, deploymentMode, sessionStatus, collection, package, customHeaders, cancellationToken),
                    logger: this.logger);
            }


            /// <inheritdoc/>
            public async Task<HttpOperationResponse<SimulatorSessionResponse>> CreateWithHttpMessagesAsync(string workspaceName, SimulatorInterface body, Dictionary<string, List<string>> customHeaders = null, CancellationToken cancellationToken = default(CancellationToken))
            {
                return await WrapSessionOperation<HttpOperationResponse<SimulatorSessionResponse>>(
                    "Create",
                    async () => {
                        HttpOperationResponse<SimulatorSessionResponse> response = await this.realOps.CreateWithHttpMessagesAsync(workspaceName, body, customHeaders, cancellationToken);
                        SimulatorSessionResponse newSession = response.Body;
                        this.logger.LogInformation($"Created session {newSession.SessionId}");
                        return response;
                    },
                    logger: this.logger
                );
            }

            /// <inheritdoc/>
            public async Task<HttpOperationResponse<SimulatorSessionResponse>> GetWithHttpMessagesAsync(string workspaceName, string sessionId, Dictionary<string, List<string>> customHeaders = null, CancellationToken cancellationToken = default(CancellationToken))
            {
                return await WrapSessionOperation<HttpOperationResponse<SimulatorSessionResponse>>(
                    "Get",
                    async () => await this.realOps.GetWithHttpMessagesAsync(workspaceName, sessionId, customHeaders, cancellationToken),
                    logger: this.logger
                );
            }

            /// <inheritdoc/>
            public async Task<HttpOperationResponse> DeleteWithHttpMessagesAsync(string workspaceName, string sessionId, Dictionary<string, List<string>> customHeaders = null, CancellationToken cancellationToken = default(CancellationToken))
            {
                return await WrapSessionOperation<HttpOperationResponse>(
                    "Delete",
                    async () => await this.realOps.DeleteWithHttpMessagesAsync(workspaceName, sessionId, customHeaders, cancellationToken),
                    logger: this.logger
                );
            }

            /// <inheritdoc/>
            public async Task<HttpOperationResponse<EventModel>> GetMostRecentActionWithHttpMessagesAsync(string workspaceName, string sessionId, Dictionary<string, List<string>> customHeaders = null, CancellationToken cancellationToken = default(CancellationToken))
            {
                return await WrapSessionOperation<HttpOperationResponse<EventModel>>(
                    "GetMostRecentAction",
                    async () => await this.realOps.GetMostRecentActionWithHttpMessagesAsync(workspaceName, sessionId, customHeaders, cancellationToken),
                    logger: this.logger
                );
            }

            /// <inheritdoc/>
            public async Task<HttpOperationResponse<EventModel>> AdvanceWithHttpMessagesAsync(string workspaceName, string sessionId, SimulatorState body, Dictionary<string, List<string>> customHeaders = null, CancellationToken cancellationToken = default(CancellationToken))
            {
                return await WrapSessionOperation<HttpOperationResponse<EventModel>>(
                    "Advance",
                    async () => {
                        HttpOperationResponse<EventModel> response = await this.realOps.AdvanceWithHttpMessagesAsync(workspaceName, sessionId, body, customHeaders, cancellationToken);
                        EventModel eventModel = response.Body;
                        if (eventModel.Type == EventType.Unregister)
                        {
                            this.logger.LogInformation($"Simulator {sessionId} received Unregister message from platform because '{eventModel.Unregister.Reason}' with details '{eventModel.Unregister.Details}'");
                        }
                        return response;
                    },
                    logger: this.logger
                );
            }
        }
    }
}