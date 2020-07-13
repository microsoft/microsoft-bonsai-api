// ------------------------------------------------------------
//  Copyright (c) Microsoft Corporation.  All rights reserved.
//  Author: maygup
//  Date: 06/23/2020
// ------------------------------------------------------------

namespace Microsoft.Bonsai.SimulatorApi.Client
{
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
        public string Workspace;

        /// <summary>
        /// AccessKey for your bonsai workspace, for authentication with the platform.
        /// </summary>
        public string AccessKey;

        /// <summary>
        /// Flag to indicate if you want to enable verbose logging to debug.
        /// </summary>
        public bool EnableLogging;

        /// <summary>
        /// Bonsai API Server URL.
        /// </summary>
        public string Server;

        /// <summary>
        /// SimulatorContext string, that needs to be passed while creating SimulatorSession.
        /// This is opaque string and you don't need to worry, but make sure, you pass it during sim creation.
        /// </summary>
        public string SimulatorContext;

        public BonsaiClientConfig(string workspace, string accessKey = "", bool enableLogging = false)
        {
            this.Workspace = System.Environment.GetEnvironmentVariable("SIM_WORKSPACE");
            this.AccessKey = System.Environment.GetEnvironmentVariable("SIM_ACCESS_KEY");
            this.SimulatorContext = System.Environment.GetEnvironmentVariable("SIM_CONTEXT");
            this.Server = System.Environment.GetEnvironmentVariable("SIM_API_HOST") ?? "https://api.bons.ai";

            this.Workspace = string.IsNullOrEmpty(workspace) ? this.Workspace : workspace;
            this.AccessKey = string.IsNullOrEmpty(accessKey) ? this.AccessKey : accessKey;

            this.EnableLogging = enableLogging;
        }
    }
}
