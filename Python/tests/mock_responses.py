"""
Mock simulator gateway responses
"""

MOCK_REGISTRATION_RESPONSE = {
    "sessionId": "0123",
    "interface": {},
    "simulatorContext": {},
    "registrationTime": "2020-01-01T17:24:34.186309100Z",
    "lastSeenTime": "2020-04-20T17:24:34.186309100Z",
    "iterationRate": 0,
    "details": "",
    "sessionStatus": "Attachable",
    "sessionProgress": {},
}

MOCK_IDLE_RESPONSE = {
    "type": "Idle",
    "sessionId": "0123",
    "sequenceId": "1",
    "idle": {},
}

MOCK_UNREGISTER_RESPONSE = {
    "type": "Unregister",
    "sessionId": "0123",
    "sequenceId": "1",
    "unregister": {"reason": "Finished", "details": "Some details"},
}

MOCK_EPISODE_START_RESPONSE = {
    "type": "EpisodeStart",
    "sessionId": "0123",
    "sequenceId": "1",
    "episodeStart": {"config": {},},
}

MOCK_EPISODE_STEP_RESPONSE = {
    "type": "EpisodeStep",
    "sessionId": "0123",
    "sequenceId": "1",
    "episodeStep": {"action": {},},
}

MOCK_EPISODE_FINISH_RESPONSE = {
    "type": "EpisodeFinish",
    "sessionId": "0123",
    "sequenceId": "1",
    "episodeFinish": {"reason": "Unspecified",},
}
