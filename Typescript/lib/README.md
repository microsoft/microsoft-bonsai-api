## An isomorphic javascript sdk for - SimulatorAPI

This package contains an isomorphic SDK for SimulatorAPI.

### Currently supported environments

- Node.js version 6.x.x or higher
- Browser JavaScript

### How to Install (not available yet, install from source in the meantime)

```bash
npm install microsoft-bonsai-api
```

##### Sample code

```typescript
import { Simulator } from 'microsoft-bonsai-api'

const config = new Simulator.Client.BonsaiClientConfig();
const client = new Simulator.Client.BonsaiClient(config);

const simInterface: Simulator.Generated.SimulatorAPIModels.SimulatorInterface = {
    name: 'mySim',
};

client.session.create(config.workspace, simInterface).then((resp) => {
    if (resp._response.status == 201) {
        // Advance sim
    } else {
        // Error
    }
});
```
