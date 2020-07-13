package microsoft.bonsai.client;

/**
 * Manages configuration for connecting to the Bonsai platform
 */
public class BonsaiClientConfig {
    
     /**
     * The Bonsai accessKey.
     */
    String accessKey;

     /**
     * The connection context details
     */
    //required, but the system will handle it
    public String simulatorContext = "";

    /**
     * The url of the server
     */
    public String server = "https://api.bons.ai/";

    /**
     * The unique Bonsai workspace
     */
    public String workspace;

    /**
     * Initializes an instance of BonsaiClientConfig class using workspace and accessKey.
     *
     * @param workspace the user's Bonsai workspace ID
     * @param accessKey the user's access key
     */
    public BonsaiClientConfig(String workspace, String accessKey) throws IllegalArgumentException, Exception {
        
        String WORKSPACE_ENV = "SIM_WORKSPACE";
        String ACCESS_KEY_ENV = "SIM_ACCESS_KEY";
        String SIM_CONTEXT_ENV = "SIM_CONTEXT";
        String SERVER_ENV = "SIM_API_HOST";

        if (System.getenv(WORKSPACE_ENV) != null) {
			this.workspace = System.getenv(WORKSPACE_ENV);
        }
        else
        {
            this.workspace = workspace;
        }

        if (System.getenv(ACCESS_KEY_ENV) != null) 
            this.accessKey = System.getenv(ACCESS_KEY_ENV);
        else
            this.accessKey = accessKey;
    

        if(this.workspace.isBlank())
            throw new IllegalArgumentException("Must pass a workspace value ");

        if(this.accessKey.isBlank())
            throw new IllegalArgumentException("Must pass an accessKey value ");
        
        if (System.getenv(SIM_CONTEXT_ENV) != null) {
			this.simulatorContext = System.getenv(SIM_CONTEXT_ENV);
        }
        
        if (System.getenv(SERVER_ENV) != null) {
			this.server = System.getenv(SERVER_ENV);
        }
        
    }
}