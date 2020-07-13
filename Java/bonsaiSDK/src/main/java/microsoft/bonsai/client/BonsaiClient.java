package microsoft.bonsai.client;

import com.microsoft.rest.RestClient;
import com.microsoft.rest.ServiceResponseBuilder;
import com.microsoft.rest.serializer.JacksonAdapter;
import microsoft.bonsai.simulatorapi.Sessions;
import microsoft.bonsai.simulatorapi.implementation.SimulatorAPIImpl;

/**
 * Manages connecting to the Bonsai platform
 */
public class BonsaiClient  {

    private RestClient restClient;
    private SimulatorAPIImpl client;

    /**
     * Gets the Sessions object to access its operations.
     * @return the Sessions object.
     */
    public Sessions sessions()
    {
        return this.client.sessions();
    }

    /**
     * Initializes the BonsaiClient class with the appropriate Authorization header
     * @param config the BonsaiClientConfig object to use for setting up connection to the Bonsai platform
     */
    public BonsaiClient(BonsaiClientConfig config) throws IllegalArgumentException,Exception
    {
        if(config == null)
        {
            throw new IllegalArgumentException("config is required");
        }

        if(config.server == null || config.server.isEmpty())
            throw new IllegalArgumentException("config.server is required");

        this.restClient = new RestClient.Builder()
                                        .withBaseUrl(config.server)
                                        .withSerializerAdapter(new JacksonAdapter())
                                        .withResponseBuilderFactory(new ServiceResponseBuilder.Factory())
                                        .build();

        // add the Authorization header
        this.restClient.headers().addHeader("Authorization", config.accessKey);
    
        this.client = new SimulatorAPIImpl(this.restClient);
    }

}