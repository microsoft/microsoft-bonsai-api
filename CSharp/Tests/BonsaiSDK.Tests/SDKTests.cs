//------------------------------------------------------------
// Copyright (c) 2019 Microsoft Corporation.  All rights reserved.
//------------------------------------------------------------

namespace BonsaiSDK.Tests
{
    using Microsoft.Bonsai.SimulatorApi;
    using Microsoft.Bonsai.SimulatorApi.Client;
    using Microsoft.Bonsai.SimulatorApi.Models;
    using Xunit;

    public class SDKTests
    {
        private BonsaiClientConfig config;
        private BonsaiClient client;

        public SDKTests()
        {
            this.config = new BonsaiClientConfig(workspace: "9711cf50-5a25-4c4a-aa3a-2c75a2919165",
                                            enableLogging: true);

            this.client = new BonsaiClient(config);
        }

        [Fact]
        public void TestSessionCreateGetAndDelete()
        {
            SimulatorInterface createBody = new SimulatorInterface(name: "sim");

            SimulatorSessionResponse createResponse = this.client.Session.CreateAsync(config.Workspace, createBody).Result;
            Assert.NotNull(createResponse);
            Assert.NotEmpty(createResponse.SessionId);

            SimulatorSessionResponse getResponse = this.client.Session.GetAsync(config.Workspace, createResponse.SessionId).Result;
            Assert.NotNull(getResponse);
            Assert.Equal(getResponse.SessionId, createResponse.SessionId);

            this.client.Session.DeleteAsync(config.Workspace, createResponse.SessionId).Wait();
        }

        [Fact]
        public void TestSessionAdvance()
        {
            SimulatorInterface createBody = new SimulatorInterface(name: "sim");

            SimulatorSessionResponse createResponse = this.client.Session.CreateAsync(config.Workspace, createBody).Result;
            Assert.NotNull(createResponse);
            Assert.NotEmpty(createResponse.SessionId);

            SimulatorState advanceBody = new SimulatorState(sequenceId: 1, state: new { number1 = 1, number2 = 2 } );
            EventModel advanceResponse = this.client.Session.AdvanceAsync(config.Workspace, createResponse.SessionId, advanceBody).Result;
            Assert.True(advanceResponse.Type == EventType.Idle);
            Assert.NotNull(advanceResponse.Idle);

            this.client.Session.DeleteAsync(config.Workspace, createResponse.SessionId).Wait();
        }
    }
}
