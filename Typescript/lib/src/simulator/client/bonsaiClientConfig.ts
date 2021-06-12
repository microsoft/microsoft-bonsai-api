/*
 * bonsaiClientConfig.ts
 *
 * Configuration for BonsaiClient
 *
 * Copyright: (c) Microsoft. All rights reserved.
 */

import { v4 as uuidv4 } from 'uuid';

export class BonsaiClientConfig {
    server: string;
    workspace: string;
    accessKey: string;
    simulatorContext: string;
    constructor(workspace = '', accessKey = '') {
        this.server = process.env.SIM_API_HOST || 'https://api.bons.ai';
        this.workspace = process.env.SIM_WORKSPACE || workspace;
        this.accessKey = process.env.SIM_ACCESS_KEY || accessKey;
        this.simulatorContext = process.env.SIM_CONTEXT || JSON.stringify({ simulatorClientId: uuidv4() });

        const args = process.argv.slice(2);
        args.forEach((val) => {
            const splitArgs = val.split('=');
            if (splitArgs.length == 2) {
                switch (splitArgs[0]) {
                    case '--accesskey':
                        this.accessKey = splitArgs[1];
                        break;
                    case '--workspace':
                        this.workspace = splitArgs[1];
                        break;
                    case '--sim-context':
                        this.simulatorContext = splitArgs[1];
                        break;
                }
            }
        });
    }
}
