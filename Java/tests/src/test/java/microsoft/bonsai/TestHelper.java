package microsoft.bonsai;

public class TestHelper {
    
    public static String getWorkspace() {

		if (System.getenv("SIM_WORKSPACE") != null) {
			return System.getenv("SIM_WORKSPACE");
		}

		return "<WORKSPACE>";
    }
    
    public static String getAccessKey() {

		if (System.getenv("SIM_ACCESS_KEY") != null) {
			return System.getenv("SIM_ACCESS_KEY");
		}

		return "<ACCESS_KEY>";
	}
}