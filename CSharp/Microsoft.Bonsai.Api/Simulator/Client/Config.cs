// ------------------------------------------------------------
//  Copyright (c) Microsoft Corporation.  All rights reserved.
//  Author: maygup
//  Date: 06/23/2020
// ------------------------------------------------------------

namespace Microsoft.Bonsai.SimulatorApi.Client
{
    using System;
    using System.Security;

    /// <summary>
    /// Configuration information needed to connect to the service.
    /// It will automatically read environment variables and set the config. You can use these setting later for calling APIs.
    /// You can set these environment variables:
    /// SIM_WORKSPACE: Bonsai workspace.false
    /// SIM_ACCESS_KEY: Bonsai access key.
    /// </summary>
    public class BonsaiClientConfig
    {
        /// <summary>
        /// bonsai workspace.
        /// </summary>
        public string Workspace { get; set; }

        /// <summary>
        /// AccessKey for your bonsai workspace, for authentication with the platform.
        /// </summary>
        public string AccessKey { get; set; }

        /// <summary>
        /// Flag to indicate if you want to enable verbose logging to debug.
        /// </summary>
        public bool EnableLogging { get; set; }

        /// <summary>
        /// Bonsai API Server URL.
        /// </summary>
        public string Server { get; set; }

        /// <summary>
        /// SimulatorContext string, that needs to be passed while creating SimulatorSession.
        /// This is opaque string and you don't need to worry, but make sure, you pass it during sim creation.
        /// </summary>
        public string SimulatorContext { get; set; }

        /// <summary>
        /// True/False indicating to use an exported brain
        /// </summary>
        public bool UseExportedBrain { get; set; }

        /// <summary>
        /// True/False indicating to use an exported brain
        /// </summary>
        public int ExportedBrainClientTimeout { get; set; }

        public BonsaiClientConfig(string workspace, string accessKey = "", bool enableLogging = false)
        {
            this.Workspace = System.Environment.GetEnvironmentVariable("SIM_WORKSPACE");
            this.AccessKey = System.Environment.GetEnvironmentVariable("SIM_ACCESS_KEY");
            this.SimulatorContext = System.Environment.GetEnvironmentVariable("SIM_CONTEXT");
            this.Server = System.Environment.GetEnvironmentVariable("SIM_API_HOST") ?? "https://api.bons.ai";

            this.Workspace = string.IsNullOrEmpty(workspace) ? this.Workspace : workspace;
            this.AccessKey = string.IsNullOrEmpty(accessKey) ? this.AccessKey : accessKey;

            if (string.IsNullOrEmpty(this.SimulatorContext))
            {
                string clientId = Guid.NewGuid().ToString("N");
                this.SimulatorContext = $"{{ \"simulatorClientId\": \"{clientId}\" }}";
            }

            this.EnableLogging = enableLogging;
        }

        /// <summary>
        /// Configure the SDK to use the exported brain
        /// </summary>
        /// <param name="exportedBrainUrl">The URL for the exported brain</param>
        public BonsaiClientConfig(string exportedBrainUrl)
        {
            this.UseExportedBrain = true;
            this.Server = exportedBrainUrl;
            this.UseClientSecret = false;
        }

        /// <summary>
        /// Configure the SDK to use the exported brain
        /// </summary>
        /// <param name="exportedBrainUrl">The URL for the exported brain</param>
        public BonsaiClientConfig(string oauthTokenGrantingUri, string applicationId, string clientSecret, string exportedBrainUrl)
        {
            this.UseClientSecret = true;
            this.ApplicationId = applicationId;
            this.ClientSecret = clientSecret;
            this.TokenGrantingAddress = oauthTokenGrantingUri;
            this.UseExportedBrain = true;
            this.Server = exportedBrainUrl;
        }

        public string TokenGrantingAddress { get; set; }
        public string ApplicationId { get; set; }
        
        // use SecureString?
        public string ClientSecret { get; set; }

        public bool UseClientSecret { get; set; }
    }
}
