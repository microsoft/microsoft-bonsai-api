/*
 * BonsaiClient.test.ts
 *
 * Tests for the Client Class.
 * TODO: Unit tests for register/advance sims
 */

import { BonsaiClient } from '../src/simulator/client/bonsaiClient';
import { BonsaiClientConfig } from '../src/simulator/client/bonsaiClientConfig';

test('Client constructor', async () => {
    const config = new BonsaiClientConfig('workspace', '111');
    const client = new BonsaiClient(config);

    expect(client._headers).toStrictEqual({
        Authorization: config.accessKey,
    });
});
