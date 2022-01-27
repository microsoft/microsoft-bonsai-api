/*
 * adder.ts
 *
 * Simple adder sim using typescript SDK
 *
 * Copyright: (c) Microsoft. All rights reserved.
 */

import { Simulator } from 'microsoft-bonsai-api';

interface AdderState {
    value1: number;
    value2: number;
    _reward: number;
}

function main() {
    const config = new Simulator.Client.BonsaiClientConfig();
    const client = new Simulator.Client.BonsaiClient(config);

    //
    // SimInterface contains all the information, that can be passed during sim session creation.
    // apart from name, simulatorContext and timeout, user can also pass optional description and capabilities here.
    //
    const simInterface: Simulator.Generated.SimulatorAPIModels.SimulatorInterface = {
        name: 'adder',
        simulatorContext: config.simulatorContext,
        timeout: 10,
    };

    log('Attempting to register simulator');
    client.session.create(config.workspace, simInterface).then((resp) => {
        log('Received Registration Response');
        if (resp._response.status == 201) {
            const sequenceId = 1;
            const simState: Simulator.Generated.SimulatorAPIModels.SimulatorState = {
                sequenceId,
                state: resetState(),
            };
            advance(client, config.workspace, resp.sessionId, simState);
        }
    });
}

function advance(
    client: Simulator.Client.BonsaiClient,
    workspace: string,
    sessionId: string,
    simState: Simulator.Generated.SimulatorAPIModels.SimulatorState
) {
    log('Attempting to advance simulator');
    client.session.advance(workspace, sessionId, simState).then((resp) => {
        if (resp._response.status === 200) {
            log(resp);

            let state: AdderState = simState.state;
            if (resp.type === 'Idle') {
                // #TODO: sleep
                log('Idle received');
            } else if (resp.type === 'EpisodeStart') {
                log('Episode Start');
                state = resetState();
            } else if (resp.type === 'EpisodeStep' && resp.episodeStep && resp.episodeStep.action) {
                log('Episode Step');
                if (resp.episodeStep.action['sum'] == (state.value1 + state.value2) % 10) {
                    state._reward = 1;
                } else {
                    state._reward = 0;
                }

                state.value1 = state.value1 += 2;
                if (state.value1 > 9) {
                    state.value1 = state.value1 -= 10;
                }

                state.value2 = state.value2 += 3;
                if (state.value2 > 9) {
                    state.value2 = state.value2 -= 10;
                }
            } else if (resp.type === 'EpisodeFinish') {
                log('Episode Finish');
            } else if (resp.type === 'Unregister') {
                log('Attempting to unregister simulator');
                client.session.deleteMethod(workspace, sessionId).then((resp) => {
                    if (resp._response.status === 204) {
                        log('Successfully Unregistered');
                    } else {
                        log(`Unable to unregister, received a ${resp._response.status} status code`);
                    }
                });
                return;
            }

            log('Advancing with following state: ' + JSON.stringify(state));
            const newState: Simulator.Generated.SimulatorAPIModels.SimulatorState = {
                sequenceId: resp.sequenceId,
                state,
            };
            advance(client, workspace, sessionId, newState);
        }
    });
}

function resetState(): AdderState {
    return {
        value1: 2,
        value2: 5,
        _reward: 0,
    };
}

function log(msg: string | Object) {
    const date = new Date();
    const dateString =
        date.getUTCFullYear() +
        '-' +
        (date.getUTCMonth() + 1) +
        '-' +
        date.getUTCDate() +
        ' ' +
        date.getUTCHours() +
        ':' +
        date.getUTCMinutes() +
        ':' +
        date.getUTCSeconds();
    console.log(`[${dateString}]:`, msg);
}

main();
