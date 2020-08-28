/*
 * bonsaiClient.ts
 *
 * Client object that handles connection to the bonsai platform
 *
 * Copyright: (c) Microsoft. All rights reserved.
 */

import * as Models from '../generated/models';
import { SimulatorAPI } from '../generated/simulatorAPI';
import { BonsaiClientConfig } from './bonsaiClientConfig';
import { OperationArguments, ServiceCallback, OperationSpec, RestResponse } from '@azure/ms-rest-js';

export class BonsaiClient extends SimulatorAPI {
    _headers: { [key: string]: any };
    constructor(config: BonsaiClientConfig, options?: Models.SimulatorAPIOptions) {
        super(options);
        this._headers = {
            Authorization: config.accessKey,
        };
    }

    sendOperationRequest(
        operationArguments: OperationArguments,
        operationSpec: OperationSpec,
        callback?: ServiceCallback<any>
    ): Promise<RestResponse> {
        if (operationArguments.options === undefined) {
            operationArguments.options = {};
        }
        operationArguments.options.customHeaders = this._headers;
        return super.sendOperationRequest(operationArguments, operationSpec, callback);
    }
}
