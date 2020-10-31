inkling "2.0"
 
using Number
using Math

#*******************************************************************
#SIMULATOR
#Definition of simulator without config
simulator Simulator(action: Action): SimState {
    #package "Headless_Sim_v01_1006"
    #package "Headless_Sim_v01_1006_1min"
    #package "Headless_v01_1013"
    #package "Without_Terminal_Condition"
    #package "With_Terminal_Condition"
    package "20201029_houseenergy_bnsf_ink"
}

#******************************************************
#STATES
#DATA TYPES FOR THE INPUT STATE SPACE
#Segment 
type Segment {
    numCranes: number,
    placeUnitUrgency: number,
    placeChassisUrgency: number,
    clearingActivitiesUrgency: number,
}
#Striptrack with 5 segments
type StripTrackA {
       numHostlers: number,
       segments: Segment[5],
}

#Striptrack with 3 segments
type StripTrackB {
        numHostlers: number,
        segments: Segment[3],
}
#STATE SPACE: 164 states
#what we receive from the sim but not necesarally the BRAIN see it. 
type SimState {
    numHostlers:number,
    stripTrack1: StripTrackB,
    stripTrack2: StripTrackB,
    stripTrack3: StripTrackB,
    stripTrack4: StripTrackB, 
    stripTrack5: StripTrackB,
    stripTrack6: StripTrackA,
    stripTrack7: StripTrackA,
    stripTrack8: StripTrackA,
    stripTrack9: StripTrackA,
    otr: number <0.0 .. 1.0>,
    otp: number <0.0 .. 1.0>,
    time: number,
    lpch: number <0.0 .. 1.0>, 
    mphh: number <0.0 .. 1.0>,
    lpch_cummulative: number,
    mphh_cummulative: number,
    otr_enabler:number <0.0 .. 1.0>,
    otp_enabler:number <0.0 .. 1.0>,
    clearing_bonus:number <0.0 .. 1.0>,
    delay_flag: number <False=0, True=1>,
}
#what the brain sees during training
type ObservationState {
    numHostlers:number,
    stripTrack1: StripTrackB,
    stripTrack2: StripTrackB,
    stripTrack3: StripTrackB,
    stripTrack4: StripTrackB, 
    stripTrack5: StripTrackB,
    stripTrack6: StripTrackA,
    stripTrack7: StripTrackA,
    stripTrack8: StripTrackA,
    stripTrack9: StripTrackA,
    otr_enabler: number,
    otp_enabler: number,
    clearing_bonus:number,
    mphh:number,
    lpch:number,
}

#******************************************************
#ACTIONS
#DATA TYPES FOR THE OUTPUT ACTION SPACE 175 actions
#Segment action vars.
type SegmentOut {
    trackSectionPriority: number <0 .. 10>,
    trackSectionAmountOfWork: number<0 .. 10>,
    effectivenessRatio: number<0.0 .. 1.0>,
    }
#striptrack with four segments
type StripTrackOutA {
segmentsOut: SegmentOut[5]
}
#striptrack with three segments
type StripTrackOutB {
segmentsOut: SegmentOut[3]
}
#ACTION SPACE
type Action {	
    stripTrack1: StripTrackOutB,
    stripTrack2: StripTrackOutB,
    stripTrack3: StripTrackOutB,
    stripTrack4: StripTrackOutB, 
    stripTrack5: StripTrackOutB,
    stripTrack6: StripTrackOutA,
    stripTrack7: StripTrackOutA,
    stripTrack8: StripTrackOutA,
    stripTrack9: StripTrackOutA
}

#******************************************************
#REWARD 
function Reward(obs: SimState, act:Action) { 
    #variables
    var brain_reward: number
    brain_reward=10*(obs.lpch*obs.mphh)
    return brain_reward 
}

#******************************************************
#TERMINAL CONDITIONS

#train delay more than certain limit
function delay_limit (d: number, max_delay: number){
    var delay_cond = false
    if d > max_delay{
        delay_cond = true
    }
    return delay_cond
}

#simulation time longer than certain limit
function time_limit (t: number,max_sim_time: number){
    var terminal_cond=false
    if (t >= max_sim_time){
        terminal_cond=true   
    }
    return terminal_cond
}

#General terminal condition
function Terminal(obs: SimState, a:Action){
    #initiate terminal conditions 
    var time_cond=false
    var terminate_episode=false
    var MAX_SIM_TIME = 235

    time_cond=time_limit(obs.time,MAX_SIM_TIME)

    #TERMINATION CONDITIONS
    terminate_episode=time_cond
    return terminate_episode
}

#**************************************************************
#CONCEPT
graph (input: ObservationState): Action {
    concept efficiency_and_effectiveness_hub(input): Action {
        curriculum {
            algorithm {
                Algorithm: "SAC",
            }
            source Simulator
            reward Reward
            terminal Terminal
            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 800,
                NoProgressIterationLimit:500000,
                }
            }
        }
    output efficiency_and_effectiveness_hub
}