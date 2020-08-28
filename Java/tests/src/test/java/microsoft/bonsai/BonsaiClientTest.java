package microsoft.bonsai;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;
import microsoft.bonsai.client.*;
import microsoft.bonsai.simulatorapi.Sessions;
import microsoft.bonsai.simulatorapi.models.*;
import microsoft.bonsai.simulatorapi.models.EventTypesEventType;
import microsoft.bonsai.simulatorapi.models.ProblemDetails;
import microsoft.bonsai.simulatorapi.models.SimulatorInterface;
import microsoft.bonsai.simulatorapi.models.SimulatorSessionResponse;
import microsoft.bonsai.simulatorapi.models.SimulatorState;

/**
 * Unit test for BonsaiClient.
 */
public class BonsaiClientTest 
    extends TestCase
{
    /**
     * Create the test case
     *
     * @param testName name of the test case
     */
    public BonsaiClientTest( String testName )
    {
        super( testName );
    }

    /**
     * @return the suite of tests being tested
     */
    public static Test suite()
    {
        return new TestSuite( BonsaiClientTest.class );
    }

    /**
     * 
     * connect to and advance the client
     */
    public void testBonsaiClientAcessKey()
    {
        String workspaceName = TestHelper.getWorkspace();

        assertTrue("workspace not set correctly", workspaceName != "<WORKSPACE>");
        assertTrue("workspace not set correctly - cannot be blank", !workspaceName.isBlank());

        try
        {
            String accessKey = TestHelper.getAccessKey();

            assertTrue("accessKey not set correctly", accessKey != "<ACCESS_KEY>");
            assertTrue("accessKey not set correctly - cannot be blank", !accessKey.isBlank());
            
            String clientType = "accessKey";
            BonsaiClientConfig akConfig = new BonsaiClientConfig(workspaceName,accessKey);

            testSessionCreateGetDelete(workspaceName, akConfig, clientType);
            testSessionAdvance(workspaceName, akConfig, clientType);
        }
        catch(Exception ex)
        {
            //fail the test
            fail("could not load akConfig " + ex.getMessage());
        }
    }

     /**
     * 
     * create, get, delete sessions
     * @param workspace the Bonsai workspace ID
     * @param config the configuration to connect with
     * @param type the type of client connection (accessKey,etc)
     */
    private void testSessionCreateGetDelete(String workspace, BonsaiClientConfig config, String type)
    {
        try
        {
            BonsaiClient client = new BonsaiClient(config);
            Sessions sessions = client.sessions();

            SimulatorInterface sim_interface = new SimulatorInterface();
            sim_interface.withName("Cartpole-Java");
            sim_interface.withTimeout(60.0);
            sim_interface.withCapabilities(null);

            // minimum required
            sim_interface.withSimulatorContext(config.simulatorContext);

            // create only returns an object, so we need to check what type of object
            Object registrationResponse = sessions.create(workspace, sim_interface);

            assertNotNull(registrationResponse);

            // if we get an error during registration
            if (registrationResponse.getClass() == ProblemDetails.class) {
                ProblemDetails details = (ProblemDetails) registrationResponse;
                fail("client type " + type + " failed to connect. " + details.detail());
            }
            // successful registration
            else if (registrationResponse.getClass() == SimulatorSessionResponse.class) {
                
                SimulatorSessionResponse sessionResponse = (SimulatorSessionResponse) registrationResponse;

                assertFalse(sessionResponse.sessionId().isBlank());

                String sessionId = sessionResponse.sessionId();

                //verify we are on the same session
                SimulatorSessionResponse getSessionResponse = (SimulatorSessionResponse)  client.sessions().get(workspace, sessionId);

                assertEquals(sessionId, getSessionResponse.sessionId());

                //unregister
                client.sessions().delete(workspace, sessionId);
            }
        }
        catch(Exception ex)
        {
            fail("client type " + type + " failed. " + ex.getMessage());
        }
    }

     /**
     * 
     * create, avance, delete session
     * @param workspace the Bonsai workspace ID
     * @param config the configuration to connect with
     * @param type the type of client connection (accessKey,etc)
     */
    private void testSessionAdvance(String workspace, BonsaiClientConfig config, String type)
    {
        try
        {
            BonsaiClient client = new BonsaiClient(config);
            Sessions sessions = client.sessions();

            SimulatorInterface sim_interface = new SimulatorInterface();
            sim_interface.withName("Cartpole-Java");
            sim_interface.withTimeout(60.0);
            sim_interface.withCapabilities(null);

            // minimum required
            sim_interface.withSimulatorContext(config.simulatorContext);

            // create only returns an object, so we need to check what type of object
            Object registrationResponse = sessions.create(workspace, sim_interface);

            assertNotNull(registrationResponse);

            // if we get an error during registration
            if (registrationResponse.getClass() == ProblemDetails.class) {
                ProblemDetails details = (ProblemDetails) registrationResponse;
                fail("client type " + type + " failed to connect. " + details.detail());
            }
            // successful registration
            else if (registrationResponse.getClass() == SimulatorSessionResponse.class) {
                
                SimulatorSessionResponse sessionResponse = (SimulatorSessionResponse) registrationResponse;

                assertFalse(sessionResponse.sessionId().isBlank());

                String sessionId = sessionResponse.sessionId();

                SimulatorState simState = new SimulatorState();
                simState.withSequenceId(1); // required
                //simState..withSessionId(sessionId); // required

                // does not need to be associated with a brain -- only for serialization and idle checks
                AdderHelper ah = new AdderHelper();
                ah.firstNumber = 1;
                ah.secondNumber = 2;

                simState.withState(ah); // required
                simState.withHalted(false); // required

                // advance only returns an object, so we need to check what type of object
                Object response = client.sessions().advance(workspace, sessionId, simState);

                // if we get an error during advance
                if (response.getClass() == ProblemDetails.class) {
                    ProblemDetails details = (ProblemDetails) response;

                    fail("client type " + type + " failed to advance. " + details.detail());
                }
                // succesful advance
                else if (response.getClass() == Event.class) {

                    Event event = (Event) response;
                    System.out.println(java.time.LocalDateTime.now() + " - received event: " + event.type());
                    
                    assertTrue(event.type() == EventType.IDLE);
                    assertNotNull(event.idle());
                    
                    client.sessions().delete(workspace, sessionId);
                    
                }
            }
        }
        catch(Exception ex)
        {
            fail("client type " + type + " failed. " + ex.getMessage());
        }
    }
}
